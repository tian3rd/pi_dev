import urllib.request
import json

def getResponse(url):
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
        data = operUrl.read()
        jsonData = json.loads(data)
    else:
        print("Error receiving data", operUrl.getcode())
    return jsonData


def main():

	urlData = "http://192.168.30.231/json"
	jsonData = getResponse(urlData)

	#for key in jsonData.keys():
	#	print(key, jsonData[key])

	print("\n")

	pm1_a = jsonData["pm1_0_atm"]
	pm1_b = jsonData["pm1_0_atm_b"]
	pm1 = (pm1_a + pm1_b) / 2.0

	pm25_a = jsonData["pm2_5_atm"]
	pm25_b = jsonData["pm2_5_atm_b"]
	pm25 = (pm25_a + pm25_b) / 2.0

	pm10_a = jsonData["pm10_0_atm"]
	pm10_b = jsonData["pm10_0_atm_b"]
	pm10 = (pm10_a + pm10_b) / 2.0

	temp_f = jsonData["current_temp_f"]
	temp_c = (temp_f - 32) / 1.8

	hum = jsonData["current_humidity"]

	dewpoint_f = jsonData["current_dewpoint_f"]
	dewpoint_c = (dewpoint_f - 32)  / 1.8

	pressure = jsonData["pressure"]

	print("PM1.0 " + str(pm1))
	print("PM2.5 " + str(pm25))
	print("PM10 " + str(pm10))

	print("Temp " + str(temp_c))
	print("Dewpoint " + str(dewpoint_c))
	print("Humidity " + str(hum))
	print("Pressure " + str(pressure))


if __name__ == '__main__':
	main()

