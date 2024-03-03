import requests
import redis
import json
import matplotlib.pyplot as plt

class CryptoDataProcessor:
    # A class for processing cryptocurrency data.
    #
    # Args:
    #     api_url (str): The URL of the API endpoint to fetch cryptocurrency data.
    #     redis_host (str): The hostname of the Redis server.
    #     redis_port (int): The port number of the Redis server.
    #     password (str): The password for the Redis server.
    #
    # Attributes:
    #     api_url (str): The URL of the API endpoint to fetch cryptocurrency data.
    #     redis_client: An instance of Redis client used for interacting with Redis database.

    def _init_(self, api_url, redis_host='redis-12779.c56.east-us.azure.cloud.redislabs.com', redis_port=12779, password='uaZAoHaiLpdIiib5Cp3HS1CSA2HnfHYL'):
        self.api_url = api_url
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=password)

    def fetch_data(self):
        # Fetch cryptocurrency data from the specified API endpoint.
        #
        # Returns:
        #     dict or None: A dictionary containing cryptocurrency data if successful, otherwise None.

        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                print("Error fetching data:", response.text)
                return None
        except Exception as e:
            print("Failed to fetch data from the API:", e)
            return None

    def insert_into_redis(self, data):
        # Insert cryptocurrency data into Redis database.
        #
        # Args:
        #     data (list): A list containing cryptocurrency data.

        for item in data:
            symbol = item['symbol']
            self.redis_client.set(symbol, str(item))

    def search_by_symbol(self, symbol):
        # Search for cryptocurrency data by symbol in Redis database.
        #
        # Args:
        #    symbol (str): The symbol of the cryptocurrency to search for.
        #
        # Returns:
        #    str: A string representation of cryptocurrency data if found, otherwise a message indicating no data found.

        data = self.redis_client.get(symbol)
        if data:
            return data.decode('utf-8')
        else:
            return f"No data found for symbol {symbol}"

    def aggregate_volumes(self):
        # Aggregate total volume of all cryptocurrencies.
        #
        # Returns:
        #     float or None: The total volume of all cryptocurrencies if data is available, otherwise None.

        data = self.fetch_data()
        if data:
            total_volume = 0.0
            for entry in data:
                total_volume += float(entry['volume'])
            return total_volume
        else:
            return None

    def plot_volumes(self):
        # Plot the top 10 volumes of cryptocurrencies.

        data = self.fetch_data()
        if data:
            sorted_data = sorted(data, key=lambda x: float(x['volume']), reverse=True)
            top_10_data = sorted_data[:10]
            symbols = []
            volumes = []
            for entry in top_10_data:
                if 'symbol' in entry and 'volume' in entry:
                    symbols.append(entry['symbol'])
                    volumes.append(float(entry['volume']))
                else:
                    print("Invalid entry found:", entry)
            plt.bar(symbols, volumes)
            plt.xlabel('Symbol')
            plt.ylabel('Volume')
            plt.title('Top 10 Volume of Crypto Currencies')
            plt.xticks(rotation=45)
            plt.show()
        else:
            print("No data to plot")

# Example usage:
if _name_ == "_main_":
    api_url = "https://api.wazirx.com/sapi/v1/tickers/24hr"
    processor = CryptoDataProcessor(api_url)
    data = processor.fetch_data()
    if data:
        processor.insert_into_redis(data)
        symbol_to_search = "btcinr"
        result = processor.search_by_symbol(symbol_to_search)
        print("Search result for symbol", symbol_to_search, ":", result)
        total_volume = processor.aggregate_volumes()
        print("Total volume of all cryptocurrencies:", total_volume)
        processor.plot_volumes()
    else:
        print("Failed to fetch data from the API.")