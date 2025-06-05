// MongoDB initialization script
db = db.getSiblingDB('event_service');

// Create collections
db.createCollection('events');

// Create indexes for better performance
db.events.createIndex({ "title": "text", "description": "text", "location": "text" });
db.events.createIndex({ "date": 1 });
db.events.createIndex({ "created_at": -1 });

// Insert sample data (optional)
db.events.insertMany([
  {
    title: "Tech Conference 2024",
    description: "Annual technology conference featuring latest innovations",
    date: "2024-07-15",
    location: "Convention Center, San Francisco",
    organizer: "Tech Events Inc.",
    capacity: 500,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    title: "Music Festival",
    description: "Three-day outdoor music festival with top artists",
    date: "2024-08-20",
    location: "Central Park, New York",
    organizer: "Music Productions",
    capacity: 10000,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('Database initialized successfully!');