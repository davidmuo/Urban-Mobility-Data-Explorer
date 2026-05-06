from flask import Blueprint, request, jsonify
from app.models import db, Trip, Zone
from sqlalchemy import func, desc
from datetime import datetime

trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

@trips_bp.route('/', methods=['GET'])
def get_trips():
    """
    Get paginated list of trips with optional filters
    ---
    tags:
      - Trips
    summary: Retrieve trips with filtering and pagination
    
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        minimum: 1
        description: Page number for pagination
        example: 1
      
      - name: per_page
        in: query
        type: integer
        required: false
        default: 100
        minimum: 1
        maximum: 1000
        description: Number of trips per page (max 1000)
        example: 50
      
      - name: start_date
        in: query
        type: string
        format: date
        required: false
        description: Filter trips starting from this date (YYYY-MM-DD)
        example: "2019-01-01"
      
      - name: end_date
        in: query
        type: string
        format: date
        required: false
        description: Filter trips up to this date (YYYY-MM-DD)
        example: "2019-01-07"
      
      - name: min_fare
        in: query
        type: number
        format: float
        required: false
        minimum: 0
        description: Minimum fare amount in USD
        example: 10.50
      
      - name: pulocation
        in: query
        type: integer
        required: false
        description: Filter by pickup location ID (see /zones endpoint)
        example: 161
    
    responses:
      200:
        description: Successful response with paginated trips
        schema:
          type: object
          required:
            - trips
            - total
            - page
            - pages
          properties:
            trips:
              type: array
              description: List of trips for current page
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Unique trip identifier
                    example: 12345
                  pickup_datetime:
                    type: string
                    format: datetime
                    description: Pickup time in ISO format
                    example: "2019-01-01T00:46:40"
                  dropoff_datetime:
                    type: string
                    format: datetime
                    description: Dropoff time in ISO format
                    example: "2019-01-01T00:53:20"
                  passenger_count:
                    type: integer
                    description: Number of passengers
                    minimum: 1
                    maximum: 9
                    example: 2
                  trip_distance:
                    type: number
                    format: float
                    description: Trip distance in miles
                    example: 3.50
                  pulocation_id:
                    type: integer
                    description: Pickup zone ID (foreign key to zones)
                    example: 161
                  dolocation_id:
                    type: integer
                    description: Dropoff zone ID (foreign key to zones)
                    example: 170
                  fare_amount:
                    type: number
                    format: float
                    description: Base fare amount in USD
                    example: 12.50
                  total_amount:
                    type: number
                    format: float
                    description: Total fare including tips/taxes in USD
                    example: 15.75
                  trip_duration_minutes:
                    type: number
                    format: float
                    description: Duration of trip in minutes (engineered feature)
                    example: 12.5
                  trip_speed_mph:
                    type: number
                    format: float
                    description: Average speed in miles per hour (engineered feature)
                    example: 16.8
                  fare_per_mile:
                    type: number
                    format: float
                    description: Fare divided by distance (engineered feature)
                    example: 3.57
                  is_weekend:
                    type: boolean
                    description: Whether trip occurred on weekend (engineered feature)
                    example: false
                  time_of_day_category:
                    type: string
                    enum: [Morning, Afternoon, Evening, Night]
                    description: Time category based on pickup hour (engineered feature)
                    example: "Evening"
            total:
              type: integer
              description: Total number of trips matching filters
              example: 15423
            page:
              type: integer
              description: Current page number
              example: 1
            pages:
              type: integer
              description: Total number of pages available
              example: 309
      
      400:
        description: Bad request - invalid parameters
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid date format. Use YYYY-MM-DD"
      
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection error"
    
    examples:
      application/json:
        {
          "trips": [
            {
              "id": 1,
              "pickup_datetime": "2019-01-01T00:46:40",
              "dropoff_datetime": "2019-01-01T00:53:20",
              "passenger_count": 1,
              "trip_distance": 1.5,
              "pulocation_id": 151,
              "dolocation_id": 239,
              "fare_amount": 7.0,
              "total_amount": 9.95,
              "trip_duration_minutes": 6.67,
              "trip_speed_mph": 13.5,
              "fare_per_mile": 4.67,
              "is_weekend": false,
              "time_of_day_category": "Night"
            }
          ],
          "total": 15423,
          "page": 1,
          "pages": 309
        }
    """
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_fare = request.args.get('min_fare', type=float)
    pulocation = request.args.get('pulocation', type=int)
    
    query = Trip.query
    
    if start_date:
        query = query.filter(Trip.pickup_datetime >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Trip.pickup_datetime <= datetime.fromisoformat(end_date))
    if min_fare:
        query = query.filter(Trip.fare_amount >= min_fare)
    if pulocation:
        query = query.filter(Trip.pulocation_id == pulocation)
    
    trips = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'trips': [trip.to_dict() for trip in trips.items],
        'total': trips.total,
        'page': page,
        'pages': trips.pages
    })

@trips_bp.route('/stats/daily', methods=['GET'])
def daily_stats():
    """
    Get daily trip statistics
    ---
    tags:
      - Trips
    parameters:
      - name: date
        in: query
        type: string
        format: date
        required: false
        default: current date
        description: Date in YYYY-MM-DD format
    responses:
      200:
        description: Daily statistics
        schema:
          type: object
          properties:
            date:
              type: string
              example: "2019-01-01"
            total_trips:
              type: integer
              example: 9891
            avg_distance:
              type: number
              format: float
              example: 2.83
            avg_fare:
              type: number
              format: float
              example: 12.55
            avg_duration:
              type: number
              format: float
              example: 17.9
            avg_speed:
              type: number
              format: float
              example: 12.51
    """
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    stats = db.session.query(
        func.count(Trip.id).label('total_trips'),
        func.avg(Trip.trip_distance).label('avg_distance'),
        func.avg(Trip.fare_amount).label('avg_fare'),
        func.avg(Trip.trip_duration_minutes).label('avg_duration'),
        func.avg(Trip.trip_speed_mph).label('avg_speed')
    ).filter(
        func.date(Trip.pickup_datetime) == date
    ).first()
    
    return jsonify({
        'date': date,
        'total_trips': stats.total_trips or 0,
        'avg_distance': f"""{round(stats.avg_distance or 0, 2)} miles""",
        'avg_fare': f"""{round(stats.avg_fare or 0, 2)} USD""",
        'avg_duration': f"""{round(stats.avg_duration or 0, 2)} minutes""",
        'avg_speed': f"""{round(stats.avg_speed or 0, 2)} mph"""
    })