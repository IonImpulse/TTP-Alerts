import time
import requests
import json
import sys

GET_ALL_LOCS = "https://ttp.cbp.dhs.gov/schedulerapi/locations/?temporary=false&inviteOnly=false&operational=true&serviceName=Global%20Entry"
'''
This returns a list of objects like
{
    "id" : 5001,
    "name" : "Hidalgo Enrollment Center",
    "shortName" : "Hidalgo Enrollment Center",
    "locationType" : "LND",
    "locationCode" : "2305",
    "address" : "Anzalduas International Bridge",
    "addressAdditional" : "5911 S. STEWART ROAD ",
    "city" : "Mission",
    "state" : "TX",
    "postalCode" : "78572",
    "countryCode" : "US",
    "tzData" : "America/Chicago",
    "phoneNumber" : "9562057929",
    "phoneAreaCode" : "",
    "phoneCountryCode" : "1",
    "phoneExtension" : "",
    "phoneAltNumber" : "9562057936",
    "phoneAltAreaCode" : "",
    "phoneAltCountryCode" : "1",
    "phoneAltExtension" : "",
    "faxNumber" : "9562057935",
    "faxAreaCode" : "",
    "faxCountryCode" : "1",
    "faxExtension" : "",
    "effectiveDate" : "2023-02-18T00:00",
    "temporary" : false,
    "inviteOnly" : false,
    "operational" : true,
    "directions" : "The Hidalgo Enrollment Center is located at the Anzalduas International Bridge.  4.6 miles South of I-2 on Bryan Road / Anzalduas Highway Mission, TX.  Look for large yellow barrels on left hand side of road.  Take road on left hand side of barrels to the public parking area. ",
    "notes" : "Arriving more than 15 minutes late to your scheduled appointment may result in being rescheduled to the next available appointment.  Please bring all necessary travel documents, proof of residency, solvency and if you have a vehicle included on your application, proof of current insurance and registration.  Due to COVID-19 a facemask will be required to be worn to enter the facility.  ",
    "mapFileName" : "/locations/5001/image",
    "remoteInd" : false,
    "services" : [ {
      "id" : 1,
      "name" : "Global Entry"
    }, {
      "id" : 3,
      "name" : "SENTRI"
    }, {
      "id" : 4,
      "name" : "U.S. / Mexico FAST"
    } ]
}
'''

GET_SPECIFIC_LOC_BY_ID = "https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&locationId="
'''
This returns a list of objects like
{
  "locationId" : 5180,
  "startTimestamp" : "2024-03-04T21:00",
  "endTimestamp" : "2024-03-04T21:10",
  "active" : true,
  "duration" : 10,
  "remoteInd" : false
}
'''

        


if __name__ == "__main__":
    print('''▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█▄▄ ▄▄█▄▄ ▄▄██ ▄▄ ███ ▄▄▀██ █████ ▄▄▄██ ▄▄▀█▄▄ ▄▄██ ▄▄▄ █
███ █████ ████ ▀▀ ███ ▀▀ ██ █████ ▄▄▄██ ▀▀▄███ ████▄▄▄▀▀█
███ █████ ████ ██████ ██ ██ ▀▀ ██ ▀▀▀██ ██ ███ ████ ▀▀▀ █
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀''')


    # Get all locations
    response = requests.get(GET_ALL_LOCS)
    locations = json.loads(response.text)

    # Print table header
    print("State\tID\tName")

    # Print out all locations, grouped by state, sorted by name
    for location in sorted(locations, key=lambda x: x['state']):
        print(f"{location['state']}\t{location['id']}\t{location['name']}")


    print("\nChoose a location ID to check for appointments.")
    
    while True:
        location_id = input("Enter ID: ")

        # Check if location ID is valid
        if not any(location['id'] == int(location_id) for location in locations):
            print("Invalid location ID. Try again.")
            continue
        else:
            break

    location_obj = next(location for location in locations if location['id'] == int(location_id))

    print(f"Selected {location_obj['name']}!")

    # Send notification on computer that script is running
    if sys.platform == "win32":
        import win10toast
        toaster = win10toast.ToastNotifier()
        toaster.show_toast("Global Entry Appointment Checker", "Running script to check for appointments...", duration=10)
    elif sys.platform == "darwin":
        import os
        os.system("osascript -e 'display notification \"Running script to check for appointments...\" with title \"Global Entry Appointment Checker\"'")
    else:
        print("Notification not supported on this platform.")

    while True:
        print("\nChecking for appointments...")

        # Get all appointments for selected location
        response = requests.get(GET_SPECIFIC_LOC_BY_ID + location_id)
        appointments = json.loads(response.text)

        # Check if there are any appointments
        if len(appointments) == 0:
            print("No appointments available. Trying again in 5 seconds...")
            time.sleep(5)
            continue
        else:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"Found {len(appointments)} appointments at {current_time}")
            
            # Print table header
            print("Date\t\t\tTime")

            # Print out all appointments, sorted by date
            # Convert to local time of the location by using the
            # timezone data in the location object

            for appointment in sorted(appointments, key=lambda x: x['startTimestamp']):
                start_time = time.strptime(appointment['startTimestamp'], "%Y-%m-%dT%H:%M")
                end_time = time.strptime(appointment['endTimestamp'], "%Y-%m-%dT%H:%M")

                print(f"{time.strftime('%m/%d/%Y', start_time)}\t{time.strftime('%I:%M %p', start_time)} - {time.strftime('%I:%M %p', end_time)}")

            # Send notification on computer
            if sys.platform == "win32":
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast("Global Entry Appointment Available", f"Found {len(appointments)} appointments at {location_obj['name']}", duration=100)
            elif sys.platform == "darwin":
                import os
                os.system(f"osascript -e 'display notification \"Found {len(appointments)} appointments at {current_time}\" with title \"Global Entry Appointment Available\"'")
            else:
                print("Notification not supported on this platform.")
        
