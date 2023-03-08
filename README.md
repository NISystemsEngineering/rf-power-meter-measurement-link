# RF Power Meter Measurement Link Service
This code implements a basic power meter measurement using the NI [MeasurementLink](https://www.ni.com/en-us/shop/electronic-test-instrumentation/application-software-for-electronic-test-and-instrumentation-category/what-is-measurementlink.html) software. This adds support for interactive measurements inside of [InstrumentStudio](https://duckduckgo.com/?q=site%3Ani.com+instrumentstudio&ia=web) and as well as supporting automation use cases.

![UI Example](/_images/UI.png)

## Getting Started
1) Ensure that you have installed the latest version of: 
    - [InstrumentStudio](https://www.ni.com/en-us/support/downloads/software-products/download.instrumentstudio.html)
    - [MeasurementLink](https://www.ni.com/en-us/support/downloads/software-products/download.measurementlink.html)
    - [Python](https://www.python.org/downloads/)
2) Run [start.bat](/RFPowerMeter/start.bat)
3) From the home screen in InstrumentStudio, select **Manual Layout**.
4) The measurement named `RF Power Meter` should appear under the *Measurements* category. Select the **Unassigned** dropdown and choose **Create large/small panel**. ![Add Measurement](/_images/AddMeasurement.png)

# Current Support
## Tested Software Versions
- MeasurementLink 2023 Q1
- InstrumentStudio 2023 Q1

## Supported Power Meters
| Name | Manufacturer | Software Link |
| ---- | ------------ | ------------- |
| NRP-Z | Rohde & Schwarz | [NRP-Z Driver](https://www.rohde-schwarz.com/driver/nrpz/) |