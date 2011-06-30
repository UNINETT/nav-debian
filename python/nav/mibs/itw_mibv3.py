# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
from twisted.internet import defer
from twisted.internet import threads

from nav.mibs import reduce_index

import mibretriever

class ItWatchDogsMibV3(mibretriever.MibRetriever):
    from nav.smidumps.itw_mibv3 import MIB as mib

    @defer.inlineCallbacks
    def can_return_sensors(self):
        defer.returnValue(False)

    def retrieve_std_columns(self):
        """ A convenient function for getting the most interesting
        columns for environment mibs. """

        return self.retrieve_columns([
                'climateSerial',
                'climateName',
                'climateAvail',
                'climateTempC',
                'climateHumidity',
                'climateLight',
                'climateAirflow',
                'climateSound',
                'climateIO1',
                'climateIO2',
                'climateIO3',
                'climateDewPointC',
                #
                'powMonSerial',
                'powMonName',
                'powMonAvail',
                'powMonKWattHrs',
                'powMonVolts',
                'powMonDeciAmps',
                'powMonRealPower',
                'powMonApparentPower',
                'powMonPowerFactor',
                'powMonOutlet1',
                'powMonOutlet2',
                #
                'tempSensorSerial',
                'tempSensorName',
                'tempSensorAvail',
                'tempSensorTempC',
                #
                'airFlowSensorSerial',
                'airFlowSensorName',
                'airFlowSensorAvail',
                'airFlowSensorTempC',
                'airFlowSensorFlow',
                'airFlowSensorHumidity',
                'airFlowSensorDewPointC',
                #
                'powerSerial',
                'powerName',
                'powerAvail',
                'powerVolts',
                'powerDeciAmps',
                'powerRealPower',
                'powerApparentPower',
                'powerApparentPower',
                'powerPowerFactor',
                #
                'doorSensorSerial',
                'doorSensorName',
                'doorSensorAvail',
                'doorSensorStatus',
                #
                'waterSensorSerial',
                'waterSensorName',
                'waterSensorAvail',
                'waterSensorDampness',
                #
                'currentMonitorSerial',
                'currentMonitorName',
                'currentMonitorAvail',
                'currentMonitorDeciAmps',
                #
                'millivoltMonitorSerial',
                'millivoltMonitorName',
                'millivoltMonitorAvail',
                'millivoltMonitorMV',
                #
                'pow3ChSerial',
                'pow3ChName',
                'pow3ChAvail',
                'pow3ChKWattHrsA',
                'pow3ChVoltsA',
                'pow3ChDeciAmpsA'
                'pow3ChVoltMaxA',
                'pow3ChVoltMinA',
                'pow3ChVoltPeakA',
                'pow3ChDeciAmpsA',
                'pow3ChRealPowerA',
                'pow3ChApparentPowerA',
                'pow3ChPowerFactorA',
                'pow3ChKWattHrsB',
                'pow3ChVoltsB',
                'pow3ChVoltMaxB',
                'pow3ChVoltMinB',
                'pow3ChVoltPeakB',
                'pow3ChDeciAmpsB',
                'pow3ChRealPowerB',
                'pow3ChApparentPowerB',
                'pow3ChPowerFactorB',
                'pow3ChKWattHrsC',
                'pow3ChVoltsC',
                'pow3ChVoltMaxC',
                'pow3ChVoltMinC',
                'pow3ChVoltPeakC',
                'pow3ChDeciAmpsC',
                'pow3ChRealPowerC',
                'pow3ChApparentPowerC',
                'pow3ChPowerFactorC',
                #
                'outletSerial',
                'outletName',
                'outletAvail',
                'outlet1Status',
                'outlet2Status',
                #
                'vsfcSerial',
                'vsfcName',
                'vsfcAvail',
                'vsfcSetPointC',
                'vsfcFanSpeed',
                'vsfcIntTempC',
                'vsfcExt1TempC',
                'vsfcExt2TempC',
                'vsfcExt3TempC',
                'vsfcExt4TempC',
                #
                'ctrl3ChSerial',
                'ctrl3ChName',
                'ctrl3ChAvail',
                'ctrl3ChVoltsA',
                'ctrl3ChVoltPeakA',
                'ctrl3ChDeciAmpsA',
                'ctrl3ChDeciAmpsPeakA',
                'ctrl3ChRealPowerA',
                'ctrl3ChApparentPowerA',
                'ctrl3ChPowerFactorA',
                'ctrl3ChVoltsB',
                'ctrl3ChVoltPeakB',
                'ctrl3ChDeciAmpsB',
                'ctrl3ChDeciAmpsPeakB',
                'ctrl3ChRealPowerB',
                'ctrl3ChApparentPowerB',
                'ctrl3ChPowerFactorB',
                'ctrl3ChVoltsC',
                'ctrl3ChVoltPeakC',
                'ctrl3ChDeciAmpsC',
                'ctrl3ChDeciAmpsPeakC',
                'ctrl3ChRealPowerC',
                'ctrl3ChApparentPowerC',
                'ctrl3ChPowerFactorC',
                #
                'ctrlGrpAmpsSerial',
                'ctrlGrpAmpsName',
                'ctrlGrpAmpsAvail',
                'ctrlGrpAmpsA',
                'ctrlGrpAmpsB',
                'ctrlGrpAmpsC',
                'ctrlGrpAmpsD',
                'ctrlGrpAmpsE',
                'ctrlGrpAmpsF',
                'ctrlGrpAmpsG',
                'ctrlGrpAmpsH',
                'ctrlGrpAmpsAVolts',
                'ctrlGrpAmpsBVolts',
                'ctrlGrpAmpsCVolts',
                'ctrlGrpAmpsDVolts',
                'ctrlGrpAmpsEVolts',
                'ctrlGrpAmpsFVolts',
                'ctrlGrpAmpsGVolts',
                'ctrlGrpAmpsHVolts',
                #
                'ctrlOutletName',
                'ctrlOutletStatus',
                'ctrlOutletFeedback',
                'ctrlOutletPending',
                'ctrlOutletDeciAmps',
                'ctrlOutletGroup',
                'ctrlOutletUpDelay',
                'ctrlOutletDwnDelay',
                'ctrlOutletRbtDelay',
                'ctrlOutletURL',
                'ctrlOutletPOAAction',
                'ctrlOutletPOADelay',
                'ctrlOutletKWattHrs',
                'ctrlOutletPower',
                #
                'dewPointSensorSerial',
                'dewPointSensorName',
                'dewPointSensorAvail',
                'dewPointSensorTempC',
                'dewPointSensorHumidity',
                'dewPointSensorDewPointC',
                #
                'digitalSensorSerial',
                'digitalSensorName',
                'digitalSensorAvail',
                'digitalSensorDigital',
                #
                'dstsSerial',
                'dstsName',
                'dstsAvail',
                'dstsVoltsA',
                'dstsDeciAmpsA',
                'dstsVoltsB',
                'dstsDeciAmpsB',
                'dstsSourceAActive',
                'dstsSourceBActive',
                'dstsPowerStatusA',
                'dstsPowerStatusB',
                'dstsSourceATempC',
                'dstsSourceBTempC',
                #
                'cpmSensorSerial',
                'cpmSensorName',
                'cpmSensorAvail',
                'cpmSensorStatus',
                #
                'smokeAlarmSerial',
                'smokeAlarmName',
                'smokeAlarmAvail',
                'smokeAlarmStatus',
                #
                'neg48VdcSensorSerial',
                'neg48VdcSensorName',
                'neg48VdcSensorAvail',
                'neg48VdcSensorVoltage',
                #
                'pos30VdcSensorSerial',
                'pos30VdcSensorName',
                'pos30VdcSensorAvail',
                'pos30VdcSensorVoltage',
                #
                'analogSensorSerial',
                'analogSensorName',
                'analogSensorAvail',
                'analogSensorAnalog',
                #
                'ctrl3ChIECSerial',
                'ctrl3ChIECName',
                'ctrl3ChIECAvail',
                'ctrl3ChIECKWattHrsA',
                'ctrl3ChIECVoltsA',
                'ctrl3ChIECVoltPeakA',
                'ctrl3ChIECDeciAmpsA',
                'ctrl3ChIECDeciAmpsPeakA',
                'ctrl3ChIECRealPowerA',
                'ctrl3ChIECApparentPowerA',
                'ctrl3ChIECPowerFactorA',
                'ctrl3ChIECKWattHrsB',
                'ctrl3ChIECVoltsB',
                'ctrl3ChIECVoltPeakB',
                'ctrl3ChIECDeciAmpsB',
                'ctrl3ChIECDeciAmpsPeakB',
                'ctrl3ChIECRealPowerB',
                'ctrl3ChIECApparentPowerB',
                'ctrl3ChIECPowerFactorB',
                'ctrl3ChIECKWattHrsC',
                'ctrl3ChIECVoltsC',
                'ctrl3ChIECVoltPeakC',
                'ctrl3ChIECDeciAmpsC',
                'ctrl3ChIECDeciAmpsPeakC',
                'ctrl3ChIECRealPowerC',
                'ctrl3ChIECApparentPowerC',
                'ctrl3ChIECPowerFactorC',
                #
                'climateRelaySerial',
                'climateRelayName',
                'climateRelayAvail',
                'climateRelayTempC',
                'climateRelayIO1',
                'climateRelayIO2',
                'climateRelayIO3',
                'climateRelayIO4',
                'climateRelayIO5',
                'climateRelayIO6',
                #
                'ctrlRelayName',
                'ctrlRelayState',
                'ctrlRelayLatchingMode',
                'ctrlRelayOverride',
                'ctrlRelayAcknowledge',
                #
                'airSpeedSwitchSensorSerial',
                'airSpeedSwitchSensorName',
                'airSpeedSwitchSensorAvail',
                'airSpeedSwitchSensorAirSpeed',
                #
                'powerDMSerial',
                'powerDMName',
                'powerDMAvail',
                'powerDMUnitInfoTitle',
                'powerDMUnitInfoVersion',
                'powerDMUnitInfoMainCount',
                'powerDMUnitInfoAuxCount',
                'powerDMChannelName1',
                'powerDMChannelName2',
                'powerDMChannelName3',
                'powerDMChannelName4',
                'powerDMChannelName5',
                'powerDMChannelName6',
                'powerDMChannelName7',
                'powerDMChannelName8',
                'powerDMChannelName9',
                'powerDMChannelName10',
                'powerDMChannelName11',
                'powerDMChannelName12',
                'powerDMChannelName13',
                'powerDMChannelName14',
                'powerDMChannelName15',
                'powerDMChannelName16',
                'powerDMChannelName17',
                'powerDMChannelName18',
                'powerDMChannelName19',
                'powerDMChannelName20',
                'powerDMChannelName21',
                'powerDMChannelName22',
                'powerDMChannelName23',
                'powerDMChannelName24',
                'powerDMChannelName25',
                'powerDMChannelName26',
                'powerDMChannelName27',
                'powerDMChannelName28',
                'powerDMChannelName29',
                'powerDMChannelName30',
                'powerDMChannelName31',
                'powerDMChannelName32',
                'powerDMChannelName33',
                'powerDMChannelName34',
                'powerDMChannelName35',
                'powerDMChannelName36',
                'powerDMChannelName37',
                'powerDMChannelName38',
                'powerDMChannelName39',
                'powerDMChannelName40',
                'powerDMChannelName41',
                'powerDMChannelName42',
                'powerDMChannelName43',
                'powerDMChannelName44',
                'powerDMChannelName45',
                'powerDMChannelName46',
                'powerDMChannelName47',
                'powerDMChannelName48',
                'powerDMChannelFriendly1',
                'powerDMChannelFriendly2',
                'powerDMChannelFriendly3',
                'powerDMChannelFriendly4',
                'powerDMChannelFriendly5',
                'powerDMChannelFriendly6',
                'powerDMChannelFriendly7',
                'powerDMChannelFriendly8',
                'powerDMChannelFriendly9',
                'powerDMChannelFriendly10',
                'powerDMChannelFriendly11',
                'powerDMChannelFriendly12',
                'powerDMChannelFriendly13',
                'powerDMChannelFriendly14',
                'powerDMChannelFriendly15',
                'powerDMChannelFriendly16',
                'powerDMChannelFriendly17',
                'powerDMChannelFriendly18',
                'powerDMChannelFriendly19',
                'powerDMChannelFriendly20',
                'powerDMChannelFriendly21',
                'powerDMChannelFriendly22',
                'powerDMChannelFriendly23',
                'powerDMChannelFriendly24',
                'powerDMChannelFriendly25',
                'powerDMChannelFriendly26',
                'powerDMChannelFriendly27',
                'powerDMChannelFriendly28',
                'powerDMChannelFriendly29',
                'powerDMChannelFriendly30',
                'powerDMChannelFriendly31',
                'powerDMChannelFriendly32',
                'powerDMChannelFriendly33',
                'powerDMChannelFriendly34',
                'powerDMChannelFriendly35',
                'powerDMChannelFriendly36',
                'powerDMChannelFriendly37',
                'powerDMChannelFriendly38',
                'powerDMChannelFriendly38',
                'powerDMChannelFriendly40',
                'powerDMChannelFriendly41',
                'powerDMChannelFriendly42',
                'powerDMChannelFriendly43',
                'powerDMChannelFriendly44',
                'powerDMChannelFriendly45',
                'powerDMChannelFriendly46',
                'powerDMChannelFriendly47',
                'powerDMChannelFriendly48',
                'powerDMChannelGroup1',
                'powerDMChannelGroup2',
                'powerDMChannelGroup3',
                'powerDMChannelGroup4',
                'powerDMChannelGroup5',
                'powerDMChannelGroup6',
                'powerDMChannelGroup7',
                'powerDMChannelGroup8',
                'powerDMChannelGroup9',
                'powerDMChannelGroup10',
                'powerDMChannelGroup11',
                'powerDMChannelGroup12',
                'powerDMChannelGroup13',
                'powerDMChannelGroup14',
                'powerDMChannelGroup15',
                'powerDMChannelGroup16',
                'powerDMChannelGroup17',
                'powerDMChannelGroup18',
                'powerDMChannelGroup19',
                'powerDMChannelGroup20',
                'powerDMChannelGroup21',
                'powerDMChannelGroup22',
                'powerDMChannelGroup23',
                'powerDMChannelGroup24',
                'powerDMChannelGroup25',
                'powerDMChannelGroup26',
                'powerDMChannelGroup27',
                'powerDMChannelGroup28',
                'powerDMChannelGroup29',
                'powerDMChannelGroup30',
                'powerDMChannelGroup31',
                'powerDMChannelGroup32',
                'powerDMChannelGroup33',
                'powerDMChannelGroup34',
                'powerDMChannelGroup35',
                'powerDMChannelGroup36',
                'powerDMChannelGroup37',
                'powerDMChannelGroup38',
                'powerDMChannelGroup39',
                'powerDMChannelGroup40',
                'powerDMChannelGroup41',
                'powerDMChannelGroup42',
                'powerDMChannelGroup43',
                'powerDMChannelGroup44',
                'powerDMChannelGroup45',
                'powerDMChannelGroup46',
                'powerDMChannelGroup47',
                'powerDMChannelGroup48',
                'powerDMDeciAmps1',
                'powerDMDeciAmps2',
                'powerDMDeciAmps3',
                'powerDMDeciAmps4',
                'powerDMDeciAmps5',
                'powerDMDeciAmps6',
                'powerDMDeciAmps7',
                'powerDMDeciAmps8',
                'powerDMDeciAmps9',
                'powerDMDeciAmps10',
                'powerDMDeciAmps11',
                'powerDMDeciAmps12',
                'powerDMDeciAmps13',
                'powerDMDeciAmps14',
                'powerDMDeciAmps15',
                'powerDMDeciAmps16',
                'powerDMDeciAmps17',
                'powerDMDeciAmps18',
                'powerDMDeciAmps19',
                'powerDMDeciAmps20',
                'powerDMDeciAmps21',
                'powerDMDeciAmps22',
                'powerDMDeciAmps23',
                'powerDMDeciAmps24',
                'powerDMDeciAmps25',
                'powerDMDeciAmps26',
                'powerDMDeciAmps27',
                'powerDMDeciAmps28',
                'powerDMDeciAmps29',
                'powerDMDeciAmps30',
                'powerDMDeciAmps31',
                'powerDMDeciAmps32',
                'powerDMDeciAmps33',
                'powerDMDeciAmps34',
                'powerDMDeciAmps35',
                'powerDMDeciAmps36',
                'powerDMDeciAmps37',
                'powerDMDeciAmps38',
                'powerDMDeciAmps39',
                'powerDMDeciAmps40',
                'powerDMDeciAmps41',
                'powerDMDeciAmps42',
                'powerDMDeciAmps43',
                'powerDMDeciAmps44',
                'powerDMDeciAmps45',
                'powerDMDeciAmps46',
                'powerDMDeciAmps47',
                'powerDMDeciAmps48',
                #
                'ioExpanderSerial',
                'ioExpanderName',
                'ioExpanderAvail',
                'ioExpanderFriendlyName1',
                'ioExpanderFriendlyName2',
                'ioExpanderFriendlyName3',
                'ioExpanderFriendlyName4',
                'ioExpanderFriendlyName5',
                'ioExpanderFriendlyName6',
                'ioExpanderFriendlyName7',
                'ioExpanderFriendlyName8',
                'ioExpanderFriendlyName9',
                'ioExpanderFriendlyName10',
                'ioExpanderFriendlyName11',
                'ioExpanderFriendlyName12',
                'ioExpanderFriendlyName13',
                'ioExpanderFriendlyName14',
                'ioExpanderFriendlyName15',
                'ioExpanderFriendlyName16',
                'ioExpanderFriendlyName17',
                'ioExpanderFriendlyName18',
                'ioExpanderFriendlyName19',
                'ioExpanderFriendlyName20',
                'ioExpanderFriendlyName21',
                'ioExpanderFriendlyName22',
                'ioExpanderFriendlyName23',
                'ioExpanderFriendlyName24',
                'ioExpanderFriendlyName25',
                'ioExpanderFriendlyName26',
                'ioExpanderFriendlyName27',
                'ioExpanderFriendlyName28',
                'ioExpanderFriendlyName29',
                'ioExpanderFriendlyName30',
                'ioExpanderFriendlyName31',
                'ioExpanderFriendlyName32',
                'ioExpanderIO1',
                'ioExpanderIO2',
                'ioExpanderIO3',
                'ioExpanderIO4',
                'ioExpanderIO5',
                'ioExpanderIO6',
                'ioExpanderIO7',
                'ioExpanderIO8',
                'ioExpanderIO9',
                'ioExpanderIO10',
                'ioExpanderIO11',
                'ioExpanderIO12',
                'ioExpanderIO13',
                'ioExpanderIO14',
                'ioExpanderIO15',
                'ioExpanderIO16',
                'ioExpanderIO17',
                'ioExpanderIO18',
                'ioExpanderIO19',
                'ioExpanderIO20',
                'ioExpanderIO21',
                'ioExpanderIO22',
                'ioExpanderIO23',
                'ioExpanderIO24',
                'ioExpanderIO25',
                'ioExpanderIO26',
                'ioExpanderIO27',
                'ioExpanderIO28',
                'ioExpanderIO29',
                'ioExpanderIO30',
                'ioExpanderIO31',
                'ioExpanderIO32',
                'ioExpanderRelayName1',
                'ioExpanderRelayState1',
                'ioExpanderRelayLatchingMode1',
                'ioExpanderRelayOverride1',
                'ioExpanderRelayAcknowledge1',
                'ioExpanderRelayName2',
                'ioExpanderRelayState2',
                'ioExpanderRelayLatchingMode2',
                'ioExpanderRelayOverride2',
                'ioExpanderRelayAcknowledge2',
                'ioExpanderRelayName3',
                'ioExpanderRelayState3',
                'ioExpanderRelayLatchingMode3',
                'ioExpanderRelayOverride3',
                'ioExpanderRelayAcknowledge3',
                ])

    def get_module_name(self):
        return self.mib.get('moduleName', None)

    @defer.inlineCallbacks
    def get_all_sensors(self):
        self.logger.error('ItWatchDogsMibV3:: get_all_sensors:  TADA!!!!')
        defer.returnValue([])
