from flask import Blueprint, jsonify
from app.models import Zone

zones_bp = Blueprint('zones', __name__, url_prefix='/api/zones')

@zones_bp.route('/', methods=['GET'])
def get_zones():
    """Get all
     taxi zones
    ---
    tags:
      - Zones
    summary: Retrieve all NYC taxi zones
    
    responses:
      200:
        description: Successful response with all zones
        schema:
          type: object
          required:
            - zones
            - total
          properties:
            zones:
              type: array
              description: List of all taxi zones
              items:
                type: object
                properties:
                  location_id:
                    type: integer
                    description: Unique identifier for the zone (matches PULocationID/DOLocationID in trips)
                    example: 1
                  borough:
                    type: string
                    description: Borough name (Manhattan, Brooklyn, Queens, Bronx, Staten Island, EWR)
                    enum: [Manhattan, Brooklyn, Queens, Bronx, "Staten Island", EWR, Unknown]
                    example: "Manhattan"
                  zone:
                    type: string
                    description: Name of the specific zone/neighborhood
                    example: "Times Square"
                  service_zone:
                    type: string
                    description: Type of taxi service zone
                    enum: ["Yellow Zone", "Boro Zone", "EWR", "Unknown"]
                    example: "Yellow Zone"
            total:
              type: integer
              description: Total number of zones
              example: 263
    
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection error"
    
    examples:
      application/json:
        {
          "zones": [
            {
              "location_id": 1,
              "borough": "EWR",
              "zone": "Newark Airport",
              "service_zone": "EWR"
            },
            {
              "location_id": 2,
              "borough": "Queens",
              "zone": "Jamaica Bay",
              "service_zone": "Boro Zone"
            },
            {
              "location_id": 4,
              "borough": "Manhattan",
              "zone": "Alphabet City",
              "service_zone": "Yellow Zone"
            }
          ],
          "total": 263
        }
        """
    zones = Zone.query.all()
    return jsonify({
        'zones': [zone.to_dict() for zone in zones],
        'total': len(zones)
    })

@zones_bp.route('/<int:location_id>', methods=['GET'])
def get_zone(location_id):
    """
    Get specific zone by ID
    ---
    tags:
      - Zones
    summary: Retrieve a single taxi zone by its location ID
    
    parameters:
      - name: location_id
        in: path
        type: integer
        required: true
        description: Unique identifier for the zone (1-265)
        minimum: 1
        maximum: 265
        example: 161
    
    responses:
      200:
        description: Zone found successfully
        schema:
          type: object
          properties:
            location_id:
              type: integer
              description: Unique identifier for the zone
              example: 161
            borough:
              type: string
              description: Borough name
              example: "Manhattan"
            zone:
              type: string
              description: Name of the specific zone/neighborhood
              example: "Midtown Center"
            service_zone:
              type: string
              description: Type of taxi service zone
              example: "Yellow Zone"
      
      404:
        description: Zone not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Zone not found"
            location_id:
              type: integer
              description: The ID that was requested
              example: 999
      
      400:
        description: Invalid location_id format
        schema:
          type: object
          properties:
            error:
              type: string
              example: "location_id must be an integer"
    
    examples:
      application/json:
        {
          "location_id": 161,
          "borough": "Manhattan",
          "zone": "Midtown Center",
          "service_zone": "Yellow Zone"
        }
    """
    zone = Zone.query.get(location_id)
    if zone:
        return jsonify(zone.to_dict())
    return jsonify({'error': 'Zone not found'}), 404