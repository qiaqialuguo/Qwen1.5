import json
import re

query = """{"vehicle_brand_name": "宝马", "vehicle_series": "X3", "vehicle_model": "2020年款", "vehicle_licensing_year": "2020", "vehicle_mileage": "10万公里"}

Now I'll call the used_car_valuation API.
Response: {valuation_result}"""
query = json.loads(re.search(r'\{.*?}', query, re.DOTALL).group(0))
print(query)