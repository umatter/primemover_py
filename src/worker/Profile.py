class Profile:
    def __init__(self):
        # Features go here


# BlockGeolocation [ PROMPT, BLOCK, ALLOW ]
# doNotTrack (0,1)
# HardwareCanvas [ REAL, BLOCK, NOISE ]
# LocalStorage & Index DB [true,false]

# Language (language: 'en-US,en;q=0.9')


# Minimum für Anlegen Multilogin-Profile:
minimum = {
"name": "%%AGENTID%%",
"os": "%%OS%%",
"browser": "%%BROWSER%%",
"network": {
"proxy": {
    "type": "%%PROXYTYPE%%",
    "host": "%%PROXYHOST",
    "port": "%%PROXYPORT%%",
    "username": "%%PROXYUSERNAME%%",
    "password": "%%PROXYPASSWORD%%"
},
"dns": []
}
}

