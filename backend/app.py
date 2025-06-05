from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# MongoDB connection
client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['DATABASE_NAME']]
events_collection = db.events


def serialize_event(event):
    """Convert MongoDB document to JSON serializable format"""
    if event:
        event['_id'] = str(event['_id'])
        return event
    return None


@app.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'description', 'date', 'location']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Create event document
        event = {
            'title': data['title'],
            'description': data['description'],
            'date': data['date'],
            'location': data['location'],
            'organizer': data.get('organizer', ''),
            'capacity': data.get('capacity', 0),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = events_collection.insert_one(event)
        event['_id'] = str(result.inserted_id)

        return jsonify({
            'message': 'Event created successfully',
            'event': serialize_event(event)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_all_events():
    try:
        events = list(events_collection.find().sort('created_at', -1))
        serialized_events = [serialize_event(event) for event in events]
        return jsonify({'events': serialized_events}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    try:
        if not ObjectId.is_valid(event_id):
            return jsonify({'error': 'Invalid event ID'}), 400

        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        return jsonify({'event': serialize_event(event)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        if not ObjectId.is_valid(event_id):
            return jsonify({'error': 'Invalid event ID'}), 400

        data = request.get_json()

        # Build update document
        update_data = {}
        allowed_fields = ['title', 'description', 'date', 'location', 'organizer', 'capacity']

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        update_data['updated_at'] = datetime.utcnow()

        result = events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Event not found'}), 404

        updated_event = events_collection.find_one({'_id': ObjectId(event_id)})
        return jsonify({
            'message': 'Event updated successfully',
            'event': serialize_event(updated_event)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        if not ObjectId.is_valid(event_id):
            return jsonify({'error': 'Invalid event ID'}), 400

        result = events_collection.delete_one({'_id': ObjectId(event_id)})

        if result.deleted_count == 0:
            return jsonify({'error': 'Event not found'}), 404

        return jsonify({'message': 'Event deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/search', methods=['GET'])
def search_events():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'events': []}), 200

        # Search in title, description, and location
        search_filter = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'location': {'$regex': query, '$options': 'i'}}
            ]
        }

        events = list(events_collection.find(search_filter).sort('created_at', -1))
        serialized_events = [serialize_event(event) for event in events]

        return jsonify({'events': serialized_events}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)