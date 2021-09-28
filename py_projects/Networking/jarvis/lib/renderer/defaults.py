DEFAULTS = {
        "logging_host": "1.1.1.1",
        "ntp_hosts": ["2.0.0.1",
                      "2.0.0.2"
                     ],
        "tacacs_hosts": ["3.0.0.1",
                         "3.0.0.2"
                        ],
        "VLAN" : {
            100: 'MANAGEMENT',
            200: 'PRODUCTION',
            300: 'NON-PRODUCTION',
            400: 'ALPHA',
            500: 'BETA'
        }
}

NODES = {
    'access.tmpl' : 'acc',
    'aggregation.tmpl' : 'agg',
    'core.tmpl': 'cor'
}

SVI = {
    'primary_pri' : 110,
    'secondary_pri': 100,
}
