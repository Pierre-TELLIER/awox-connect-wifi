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

## SSL pinning bypass

```
frida --codeshare akabe1/frida-multiple-unpinning -U -f com.awox.smart.control -l mbed.js
```

The cert files are present in

```
/data/data/com.awox.smart.control/files/SSLData/Gateware/
```

On first app lauch, the files ca.pem, client-cert.pem and client-key.pem are generated.

## Scripts

`mbed.js`

```js
var modName = "libjawGateware.so";

function toPrintable(bytes) {
    var arr = new Uint8Array(bytes);
    var out = "";
    for (var i = 0; i < arr.length; i++) {
        var b = arr[i];
        if (b >= 0x20 && b <= 0x7e) out += String.fromCharCode(b);
        else if (b === 0x0a) out += "\n";
        else if (b === 0x0d) out += "";
        else if (b === 0x00) out += "␀";
        else out += "\\x" + b.toString(16).padStart(2, "0");
    }
    return out;
}

function dumpBuffer(label, buf, len) {
    try {
        var bytes = Memory.readByteArray(buf, len);
        console.log("\n=== " + label + " (" + len + " bytes) ===");
        console.log(toPrintable(bytes));
    } catch (e) {
        console.log("[!] dump failed for " + label + ": " + e);
    }
}

function attachHooks() {
    var writeAddr = Module.findExportByName(modName, "mbedtls_ssl_write");
    var readAddr = Module.findExportByName(modName, "mbedtls_ssl_read");

    if (writeAddr) {
        Interceptor.attach(writeAddr, {
            onEnter: function (args) {
                dumpBuffer("mbedtls_ssl_write", args[1], args[2].toInt32());
            }
        });
        console.log("[+] hooked mbedtls_ssl_write");
    }
    if (readAddr) {
        Interceptor.attach(readAddr, {
            onEnter: function (args) {
                this.buf = args[1];
            },
            onLeave: function (retval) {
                var len = retval.toInt32();
                if (len > 0) dumpBuffer("mbedtls_ssl_read", this.buf, len);
            }
        });
        console.log("[+] hooked mbedtls_ssl_read");
    }
    return !!(writeAddr || readAddr);
}

// Poll until the library is actually loaded, then attach once.
var attached = false;
var interval = setInterval(function () {
    if (attached) {
        clearInterval(interval);
        return;
    }
    var mod = Process.findModuleByName(modName);
    if (mod) {
        console.log("[*] " + modName + " loaded at " + mod.base + " — attaching hooks");
        attached = attachHooks();
        if (attached) clearInterval(interval);
    }
}, 100);
```
