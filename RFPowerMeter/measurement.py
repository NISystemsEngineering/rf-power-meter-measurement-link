"""A default measurement with an array in and out."""
import logging
import pathlib
import sys
import skrf as rf
from skrf import network2

from RsInstrument import *
import click
import time
import math
import ni_measurementlink_service as nims

service_directory = pathlib.Path(__file__).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "RFPowerMeter.serviceconfig",
    version="1.0.1.0",
    ui_file_paths=[service_directory / "RFPowerMeter.measui"],
)


@measurement_service.register_measurement
@measurement_service.configuration("Resource Name", nims.DataType.String, "")
@measurement_service.configuration("Frequency (Hz)", nims.DataType.Double, 1e9)
@measurement_service.configuration("Aperture Time (s)", nims.DataType.Double, 0.01)
@measurement_service.configuration("Auto Averaging", nims.DataType.Boolean, True)
@measurement_service.configuration("Averaging Count", nims.DataType.Int32, 1)
@measurement_service.configuration("Power Offset", nims.DataType.Double, 0.0)
@measurement_service.configuration("Deembedding File Path", nims.DataType.Path, "")
@measurement_service.output("Power (dBm)", nims.DataType.Float)
def measure(resource_name,frequency,aperture_time,auto_averaging,averaging_count,power_offset,deembedding_path):

    nrpz = None
    # Make sure you have the last version of the RsInstrument
    RsInstrument.assert_minimum_version('1.53.0')
    try:
        # -----------------------------------------------------------
        # Initialization:
        # -----------------------------------------------------------
        # Adjust the VISA Resource string to fit your instrument
        nrpz = RsInstrument(resource_name, True, False)
        nrpz.visa_timeout = 3000  # Timeout for VISA Read Operations
        nrpz.instrument_status_checking = True  # Error check after each command
    except ResourceError as ex:
        measurement_service.context.abort(-1,'Error initializing the instrument session:\n' + ex.args[0])

    print(f'Visa manufacturer: {nrpz.visa_manufacturer}')
    print(f'Instrument Identification string: {nrpz.idn_string}')

    try:

        nrpz.write_str("*RST")  # Reset the instrument, clear the Error queue
        nrpz.write_str("INIT:CONT OFF")  # Switch OFF the continuous sweep
        # -----------------------------------------------------------
        # Basic Settings:
        # -----------------------------------------------------------
        nrpz.write_str('INIT:CONT OFF')
        nrpz.write_str('SENS:FUNC \"POW:AVG\"')
        nrpz.write_str(f"SENS:FREQ {frequency}")
        on_off = "ON" if auto_averaging else "OFF"
        nrpz.write_str(f"SENS:AVER:COUNT:AUTO {on_off}")
        nrpz.write_str(f"SENS:AVER:COUN {averaging_count}")
        nrpz.write_str('SENS:AVER:STAT ON')
        nrpz.write_str('SENS:AVER:TCON REP')

        nrpz.write_str(f"SENS:POW:AVG:APER {aperture_time}")
        # -----------------------------------------------------------
        # SyncPoint 'SettingsApplied' - all the settings were applied
        # -----------------------------------------------------------
        nrpz.write_str("INIT:IMM")  # Start the sweep

        offset = power_offset
        if (deembedding_path != ""):
            network = rf.Network(deembedding_path)
            freq = rf.Frequency.from_f(frequency, unit="Hz")
            single_matrix = network[freq]
            offset = single_matrix.s_db[:,1,0][0]
            print(f"using offset {offset} from s2p file")

        nrpz.write_str(f"SENS:CORR:OFFS {offset}")
        nrpz.write_str('SENS:CORR:OFFS:STAT ON')

        success = False
        for x in range(0, 200):
            status = nrpz.query_int('STAT:OPER:COND?')
            if (status & 16) == 0:
                # Status register bit 4 signals MEASURING status
                # Finished measuring, break
                success = True
                break
            time.sleep(0.02)

        if not success:
            raise TimeoutError("Measurement timed out")

        # -----------------------------------------------------------
        # Fetching the results, format does not matter, the driver function always parses it correctly
        # -----------------------------------------------------------
        nrpz.write_str('FORMAT ASCII')
        results = nrpz.query_str('FETCH?').split(',')
        power_watt = float(results[0])
        if power_watt < 0:
            power_watt = 1E-12
        power_dbm = 10 * math.log10(power_watt / 1E-3)
        print(f'Measured power: {power_watt} Watt, {power_dbm:.3f} dBm')

        # Close the session
        #nrpz.close()


        return ([power_dbm])
    except BaseException as ex:
        print(f"Logging exception {str(ex)}")
        measurement_service.context.abort(-1,str(ex))
    finally:
        nrpz.close()


@click.command
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Enable verbose logging. Repeat to increase verbosity.",
)
def main(verbose: int):
    """Host the Sample Measurement service."""
    if verbose > 1:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=level)

    with measurement_service.host_service():
        input("Press enter to close the measurement service.\n")


if __name__ == "__main__":
    main()
    sys.exit(0)
