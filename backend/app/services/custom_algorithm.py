class ManualTopRoutesAnalyzer:    
    def __init__(self, trips_data):
        self.trips_data = trips_data
        self.route_counts = {}
    
    def manual_count_routes(self):
        for trip in self.trips_data:
            route = f"{trip[0]}_{trip[1]}"
            
            if route in self.route_counts:
                self.route_counts[route] += 1
            else:
                self.route_counts[route] = 1
        
        return self.route_counts
    
    def manual_quicksort(self, arr, key_func=None):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = []
        middle = []
        right = []
        
        for item in arr:
            if key_func:
                if key_func(item) < key_func(pivot):
                    left.append(item)
                elif key_func(item) > key_func(pivot):
                    right.append(item)
                else:
                    middle.append(item)
            else:
                if item < pivot:
                    left.append(item)
                elif item > pivot:
                    right.append(item)
                else:
                    middle.append(item)
        
        return self.manual_quicksort(left, key_func) + middle + self.manual_quicksort(right, key_func)
    
    def get_top_routes(self, n=10):
        route_counts = self.manual_count_routes()
        
        route_list = [(route, count) for route, count in route_counts.items()]
        
        sorted_routes = self.manual_quicksort(
            route_list, 
            key_func=lambda x: x[1]
        )
        descending_routes = []
        for i in range(len(sorted_routes) - 1, -1, -1):
            descending_routes.append(sorted_routes[i])
        
        return descending_routes[:n]