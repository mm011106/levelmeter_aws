# levelmeter_aws
Iot Device for the level meter. AWS version

milkcocoaでやっていた内容をAWSに移します。
そのためのエッジデバイス側アプリです。

## Hardware
Raspberry Pi + AD converter(MCP3208 12bit, 4ch, SPI) + Environmental sensor (BME280 I2C)

## Use
- MCP3208read binary to communicate with the AD converter on SPI port
- bme280.py to communicate with BME280

## Which information we can get from this device
We will get :
- L-He Level of cryostat
- Container pressure
- External voltage input (for future use: exhaust gas temperature monitor)
- External voltage input (for something important)
- Ambient Temperature
- Atmospheric Pressure
- Relative Humidity

## Topic and payload
/ET/


```Payload format:JSON
{"Timestamp":"1455921413284",
  "Reading":{
      "Level":"0x0000",
      "Pressure":"0x0000",
      "aux2":"0x0000",
      "aux3":"0x0000"
      },
  "State":{
      "Temp":"23.5",
      "Humid":"50.0",
      "Atmpress":"1023",
      "HeadTemp":"15.0"
      }
  }
```

