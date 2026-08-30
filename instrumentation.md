# Documentation

## Device
All test were made on the light EgloBulb+

The phone used was a Samsung galaxy A5 2017 (`SM-A520F`), rooted with `Magisk` on `LineageOS 18.1, Android 11`


## Software
### Frida
`frida-server-16.7.19-android-arm64` was used as subsequent version made the whole phone crash


launch on the phone
```
/data/local/tmp/frida-server
```

### MITM proxy
we are capturing https data with `mitmproxy-12.2.3`

## SSL pinning bypass
Scripts should be in another branch
```
frida --codeshare akabe1/frida-multiple-unpinning -U -f com.awox.smart.control -l mbed.js
```

The cert files are present in 
```
/data/data/com.awox.smart.control/files/SSLData/Gateware/
```

On first app lauch, the files ca.pem, client-cert.pem and client-key.pem are generated. 



## Ghidra
Interesting function
```commandline
PerformSignInCommand
PerformSignOff
PerformSignOutCommand
PerformSignUp
```

