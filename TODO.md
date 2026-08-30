# TODOs

store the state of the light somewhere
received on first connexion
```commandline
␀\x1eaw/bkYXNUb44M/u/gwBEDDC2BBD988{ "rt": "oic.d.light", "href": "/v1/devices/L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "provider": "L4HActuator", "rc": 1, "t": 0, "di": "L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "n": "ESMLw-c14g-E27_C2BBD988", "links": [{ "rt": "oic.wk.p", "href": "platform", "mnmn": "AwoX", "mnmo": "ESMLw-c14g-E27", "mnfv": "1.0.7" },{ "rt": "oic.r.switch.binary", "href": "switch", "value": 0 },{ "rt": "gw.r.light.favorite", "href": "lightfavorite", "count":5 },{ "rt": "gw.r.light.mode", "href": "lightmode", "lightMode": "color" },{ "rt": "oic.r.light.dimming", "href": "lightdimming", "dimmingSetting": 73, "range": [0, 100], "step": 1 },{ "rt": "gw.r.light.temperature", "href": "lighttemperature", "temperatureSetting": 0, "range": [0, 100], "step": 1 },{ "rt": "oic.r.colour.rgb", "href": "colorrgb", "rgbValue": [0, 55, 255] },{ "rt": "gw.r.color.sequence", "href": "sequence", "id": 0, "transitionDuration":0, "colorDuration": 0 },{ "rt": "gw.r.schedule", "href": "schedule", "maxSchedules":5,"schedules":[{"id": 0, "type": "empty", "enabled": false, "d": { }},{"id": 1, "type": "empty", "enabled": false, "d": { }},{"id": 2, "type": "empty", "enabled": false, "d": { }},{"id": 3, "type": "empty", "enabled": false, "d": { }},{"id": 4, "type": "empty", "enabled": false, "d": { }}] },{ "rt": "gw.r.dio1.paired", "href": "dio1paired", "p": [-1, -1, -1, -1, -1, -1] } ] }
```

and after each request:
```raw
=== mbedtls_ssl_read (1416 bytes) ===
␀\x1eaw/bkYXNUb44M/u/gwBEDDC2BBD988{ "rt": "oic.d.light", "href": "/v1/devices/L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "provider": "L4HActuator", "rc": 1, "t": 0, "di": "L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "n": "ESMLw-c14g-E27_C2BBD988", "links": [{ "rt": "oic.wk.p", "href": "platform", "mnmn": "AwoX", "mnmo": "ESMLw-c14g-E27", "mnfv": "1.0.7" },{ "rt": "oic.r.switch.binary", "href": "switch", "value": 0 },{ "rt": "gw.r.light.favorite", "href": "lightfavorite", "count":5 },{ "rt": "gw.r.light.mode", "href": "lightmode", "lightMode": "color" },{ "rt": "oic.r.light.dimming", "href": "lightdimming", "dimmingSetting": 73, "range": [0, 100], "step": 1 },{ "rt": "gw.r.light.temperature", "href": "lighttemperature", "temperatureSetting": 0, "range": [0, 100], "step": 1 },{ "rt": "oic.r.colour.rgb", "href": "colorrgb", "rgbValue": [0, 55, 255] },{ "rt": "gw.r.color.sequence", "href": "sequence", "id": 0, "transitionDuration":0, "colorDuration": 0 },{ "rt": "gw.r.schedule", "href": "schedule", "maxSchedules":5,"schedules":[{"id": 0, "type": "empty", "enabled": false, "d": { }},{"id": 1, "type": "empty", "enabled": false, "d": { }},{"id": 2, "type": "empty", "enabled": false, "d": { }},{"id": 3, "type": "empty", "enabled": false, "d": { }},{"id": 4, "type": "empty", "enabled": false, "d": { }}] },{ "rt": "gw.r.dio1.paired", "href": "dio1paired", "p": [-1, -1, -1, -1, -1, -1] } ] }

=== mbedtls_ssl_write (310 bytes) ===
2\xb3\x02␀Caw/bkYXNUb44M/r/gwBEDDC2BBD988/e4b50c94-a450-11f1-8d37-b27f98e1dd82␀\x08{"h":"/v1/devices/L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1/lighttemperature","d":"PUT","m":"application/json","b":{"temperatureSetting":0},"o":{"id":"e4b50c94-a450-11f1-8d37-b27f98e1dd82","r":"u","t":"2026-08-30T08:59:06.741Z"}}

=== mbedtls_ssl_read (1 bytes) ===
@

=== mbedtls_ssl_read (1 bytes) ===
\x02

=== mbedtls_ssl_read (2 bytes) ===
␀\x08

=== mbedtls_ssl_write (303 bytes) ===
2\xac\x02␀Caw/bkYXNUb44M/r/gwBEDDC2BBD988/e4b50c94-a450-11f1-8d37-b27f98e1dd82␀\x09{"h":"/v1/devices/L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1/lightdimming","d":"PUT","m":"application/json","b":{"dimmingSetting":90},"o":{"id":"e4b50c94-a450-11f1-8d37-b27f98e1dd82","r":"u","t":"2026-08-30T08:59:06.741Z"}}

=== mbedtls_ssl_read (1 bytes) ===
@

=== mbedtls_ssl_read (1 bytes) ===
\x02

=== mbedtls_ssl_read (2 bytes) ===
␀\x09

=== mbedtls_ssl_read (1 bytes) ===
0

=== mbedtls_ssl_read (1 bytes) ===
\x88

=== mbedtls_ssl_read (1 bytes) ===
\x0b

=== mbedtls_ssl_read (1416 bytes) ===
␀\x1eaw/bkYXNUb44M/u/gwBEDDC2BBD988{ "rt": "oic.d.light", "href": "/v1/devices/L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "provider": "L4HActuator", "rc": 1, "t": 0, "di": "L4HActuator_0fbba001-9be5-3c03-bc3e-2cdbf906d9a1", "n": "ESMLw-c14g-E27_C2BBD988", "links": [{ "rt": "oic.wk.p", "href": "platform", "mnmn": "AwoX", "mnmo": "ESMLw-c14g-E27", "mnfv": "1.0.7" },{ "rt": "oic.r.switch.binary", "href": "switch", "value": 1 },{ "rt": "gw.r.light.favorite", "href": "lightfavorite", "count":5 },{ "rt": "gw.r.light.mode", "href": "lightmode", "lightMode": "white" },{ "rt": "oic.r.light.dimming", "href": "lightdimming", "dimmingSetting": 73, "range": [0, 100], "step": 1 },{ "rt": "gw.r.light.temperature", "href": "lighttemperature", "temperatureSetting": 0, "range": [0, 100], "step": 1 },{ "rt": "oic.r.colour.rgb", "href": "colorrgb", "rgbValue": [0, 55, 255] },{ "rt": "gw.r.color.sequence", "href": "sequence", "id": 0, "transitionDuration":0, "colorDuration": 0 },{ "rt": "gw.r.schedule", "href": "schedule", "maxSchedules":5,"schedules":[{"id": 0, "type": "empty", "enabled": false, "d": { }},{"id": 1, "type": "empty", "enabled": false, "d": { }},{"id": 2, "type": "empty", "enabled": false, "d": { }},{"id": 3, "type": "empty", "enabled": false, "d": { }},{"id": 4, "type": "empty", "enabled": false, "d": { }}] },{ "rt": "gw.r.dio1.paired", "href": "dio1paired", "p": [-1, -1, -1, -1, -1, -1] } ] }

```




