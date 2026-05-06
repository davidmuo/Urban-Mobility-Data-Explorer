from flask import Blueprint, request, jsonify
from app.services.custom_algorithm import ManualTopRoutesAnalyzer
from app.models import Trip, db

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/top-routes', methods=['GET'])
def top_routes():
    """
    Find top busiest routes
    ---
    tags:
      - Analytics
    summary: Get most frequent pickup-dropoff pairs using custom implementation
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        minimum: 1
        maximum: 100
        description: Number of top routes to return
        example: 5
      
      - name: sample_size
        in: query
        type: integer
        required: false
        default: 5000
        minimum: 100
        maximum: 50000
        description: Number of trips to analyze (for performance)
        example: 10000
    
    responses:
      200:
        description: Success - returns top routes calculated by manual algorithm
        schema:
          type: object
          required:
            - algorithm
            - top_routes
            - total_analyzed
          properties:
            
            top_routes:
              type: array
              description: List of top routes with their frequencies
              items:
                type: object
                properties:
                  route:
                    type: string
                    description: Route in format "pickup_dropoff"
                    pattern: '^\d+_\d+$'
                    example: "161_170"
                  count:
                    type: integer
                    description: Number of trips on this route
                    minimum: 1
                    example: 45
            
            total_analyzed:
              type: integer
              description: Total number of trips analyzed
              example: 5000
            
      
      400:
        description: Bad request - invalid parameters
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Limit must be between 1 and 100"
            status:
              type: integer
              example: 400
      
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Error processing algorithm"
    
    examples:
      application/json:
        {
          "algorithm": "manual quicksort + counting",
          "top_routes": [
            {
              "route": "161_170",
              "count": 45
            },
            {
              "route": "151_239", 
              "count": 38
            },
            {
              "route": "239_246",
              "count": 32
            }
          ],
          "total_analyzed": 5000,
          "algorithm_details": {
            "counting_method": "Manual dictionary counting",
            "sorting_method": "Custom quicksort implementation",
            "time_complexity": "O(n log n) average",
            "space_complexity": "O(n)"
          }
        }
    """
    
    limit = request.args.get('limit', 10, type=int)
    
    trips = Trip.query.with_entities(
        Trip.pulocation_id, Trip.dolocation_id
    ).limit(5000).all()
    
    trips_list = [(t.pulocation_id, t.dolocation_id) for t in trips]
    
    analyzer = ManualTopRoutesAnalyzer(trips_list)
    top_routes = analyzer.get_top_routes(limit)
    
    return jsonify({
        'algorithm': 'manual quicksort + counting',
        'top_routes': [
            {'route': r[0], 'count': r[1]} for r in top_routes
        ],
        'total_analyzed': len(trips_list)
    })