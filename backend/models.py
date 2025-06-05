from datetime import datetime
from typing import Optional, Dict, Any


class Event:
    def __init__(self, title: str, description: str, date: str, location: str,
                 organizer: str = "", capacity: int = 0, _id: Optional[str] = None):
        self._id = _id
        self.title = title
        self.description = description
        self.date = date
        self.location = location
        self.organizer = organizer
        self.capacity = capacity
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format"""
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'location': self.location,
            'organizer': self.organizer,
            'capacity': self.capacity,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event instance from dictionary"""
        return cls(
            title=data['title'],
            description=data['description'],
            date=data['date'],
            location=data['location'],
            organizer=data.get('organizer', ''),
            capacity=data.get('capacity', 0),
            _id=str(data.get('_id', ''))
        )

    def validate(self) -> Dict[str, str]:
        """Validate event data and return errors if any"""
        errors = {}

        if not self.title or len(self.title.strip()) == 0:
            errors['title'] = 'Title is required'
        elif len(self.title) > 200:
            errors['title'] = 'Title must be less than 200 characters'

        if not self.description or len(self.description.strip()) == 0:
            errors['description'] = 'Description is required'
        elif len(self.description) > 1000:
            errors['description'] = 'Description must be less than 1000 characters'

        if not self.date:
            errors['date'] = 'Date is required'

        if not self.location or len(self.location.strip()) == 0:
            errors['location'] = 'Location is required'
        elif len(self.location) > 200:
            errors['location'] = 'Location must be less than 200 characters'

        if self.capacity < 0:
            errors['capacity'] = 'Capacity cannot be negative'

        return errors