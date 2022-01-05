#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('reset', '')


# In[3]:


from openpyxl import load_workbook
import math
import json
import os
import sys
import math
import time
import pathlib
import numpy as np
import pandas as pd
from PIL import Image
from calendar import monthrange
from datetime import date, datetime


# In[239]:


class SolarCalculator:
    
    def __init__(self, zipCode, pmax, area_module, input_inclination, input_direction, ground_reflection_factor, least_horizon_shielding,  year, isCumstomFile = False):
        self.zipCode = zipCode
        self.pmax= pmax
        self.area_module= area_module
        self.input_inclination = input_inclination #lutning
        self.input_direction = input_direction #riktning
        self.ground_reflection_factor= ground_reflection_factor #Albedo
        self.least_horizon_shielding = least_horizon_shielding # Horisontavskärmning
        self.efficiency = pmax / area_module
        self.input_efficiency = efficiency
        self.postal_code_input = zipCode
        self.current_year = year if isCumstomFile else date.today().year
        self.year_input = self.current_year
        self.getNumberOfdaysInYearLambda = lambda year : sum([monthrange(year, month)[1] for month in range(1, 13)])
        self.number_days_in_year = self.getNumberOfdaysInYearLambda(self.current_year)
        self.totalNumberOfHoursInYear = self.number_days_in_year * 24 # days_ per_year

        # The below value are constants which are to be used for the solar calculations.
        self.longitude_time_zone = 15
        self.hay_anisotropic = 1.0
        self.height_pv_module_out_with_glass = 1
        self.pv_row_spacing = 1000
        self.correction_diffuse_shadowing = 0
        self.angle_dependent_coefficient_direct_sunlight = 4
        self.number_of_rows_pv = 1
        self.system_efficiency = 0.92 #0.912
        self.k_diff = 0.95 #0.925 // diffuse acceptance coefficient
        self.alfa = 0.004
        self.a1_heat_loss_figures_pv_modules = 25 # 20
        self.n0_thermal_solar_absorption_pv = 0.9
        self.reference_angle = -175
        self.azimuthal_array_size = int(350 / 10)
        self.day = 1
        self.time_count = 0.5

        # The below listed variables are used for the per month calculations
        self.sum_cal = 0
        self.sum_total = 0
        self.sum_unshaded = 0
        self.sum_total_unshaded = 0
        self.sum_g_direct = 0
        self.sum_g_direct_total = 0
        self.sum_g_diffuse = 0
        self.sum_g_diffuse_total = 0
        self.days_previous = 0
        self.total_count_per_month = 0
        self.sum_s = 0
        self.sum_total_s = 0
        self.sum_shaded = 0
        self.sum_total_shaded = 0
        self.month_total_unshaded = np.zeros(12, dtype=np.float64)
        self.month_total_shaded = np.zeros(12, dtype=np.float64)
        self.month_output_pv_unshaded = np.zeros(12, dtype=np.float64)
        self.month_output_pv_shaded = np.zeros(12, dtype=np.float64)
        
        self.declination = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.b = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.t_j = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.t_s = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.hour_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.inclination_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.angle_below_90 = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.solar_zenith_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.geometric_factor = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.anisotropic_index = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.direct_solar_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.solar_altitude_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.diffuse_solar_radiation_pv_planet = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.angle_of_attack = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.c_3 = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.c_2 = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.c_1 = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.pseudo_solar_azimuth_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.hour_angle_due = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.solar_azimuth_angle = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.solar_height_over_horizon = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.solar_shaded_angle_multiple_rows = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.share_fully_illuminated_pv = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.correction_shaded_multiple_pv_rows = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.total_unshaded = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.output_pv_unshaded = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.test_angle_from_lookup = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.g_dir_shaded = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.total_shaded = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.output_pv_shaded = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)
        self.asimuth_angle = np.zeros(self.azimuthal_array_size + 1, dtype=np.float64)
        self.shaded_angle = np.zeros(self.azimuthal_array_size + 1, dtype=np.float64)
        self.test_angle_lookup_condition = np.zeros(self.totalNumberOfHoursInYear, dtype=np.float64)

    def getWeekNumberAndDay(self, year, month, day):
        """
        isocalendar() returns a namedtuple with the fields year, week and weekday
        current_date = date(2022, 1, 2)
        getWeekNumberAndDay(2021, 1, 6)
        """
        #print('year=', year, 'month=', month, 'day=', day)
        weekdays = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
        current_date = date(year, month, day)
        year_out, weekNumber, weekday = current_date.isocalendar()
        #print('year_out=', year_out, 'weekNumber=', weekNumber, 'weekday=', weekday)
        return weekNumber, weekdays[weekday - 1]

    def getNumberOfdaysInMonth(self, year = datetime.now().year, month = 1):
        """
        The monthrange() method is used to get weekday of first day of the month 
        and number of days in month, for the specified year and month.
        """
        assert month >= 1 and month <= 12
        weekdays = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
        months = ['Januari', 'Februari', 'Mars', 'april', 'Maj', 'Juni', 'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December' ]
        weekday, numberDaysInMonth = monthrange(year, month)
        return numberDaysInMonth, months[month - 1], weekdays[weekday]

    def getNumberOfdaysInYear(self, year = datetime.now().year):
        #print('Year=', year)
        totalDays = 0 
        for month in range(1, 13):
            weekday, numberDaysInMonth = monthrange(year, month)
            totalDays += numberDaysInMonth
            #print(month)
        totalHours = 24 * totalDays
        return totalDays, totalHours

    def findIndex(self, asimuth_angle, element): 
        index = np.argwhere(asimuth_angle == element)
        return -1 if len(index) == 0 else index[0][0]
    
    def get_yearly_data(self, currentYear = datetime.now().year):
        totalNumberOfDays, totalNumberOfHours = self.getNumberOfdaysInYear(currentYear)
        currentMonth = 1
        day = 1
        yearlyData = [
            ['Totala Timmar', 'Timmar', 'Dag', 'Veckodag', 'Veckonummer', 'Månad',
                'Skuggad produktion', 
                'Oskuggad produktion',
                'Skuggad solstrålning', 
                'Oskuggad solstrålning']]

        for i in range(totalNumberOfHours):
            numberOfDaysInCurrentMonth, monthName, _ = self.getNumberOfdaysInMonth(currentYear, currentMonth)
            oneDayHasPassed = i % 24 == 0 and i > 0
            oneMonthHasPassed = day % numberOfDaysInCurrentMonth == 0

            if oneDayHasPassed:
                day += 1

            if oneMonthHasPassed and oneDayHasPassed:
                currentMonth += 1
                day = 1

            weekNumber, weekday = self.getWeekNumberAndDay(currentYear, currentMonth, day)
            #print([i, i % 24, day, weekday, weekNumber, monthName])
            #print('-'*20)
            prod_shaded = self.output_pv_shaded[i]
            prod_unshaded = self.output_pv_unshaded[i]
            emi_shaded = self.total_shaded[i]
            emi_unshaded = self.total_unshaded[i]

            yearlyData.append([i, i % 24, day, weekday, weekNumber, monthName, prod_shaded, prod_unshaded, emi_shaded, emi_unshaded])
        return yearlyData
    
    def compute(self, input_gh, input_gd, input_temp, lat, lon):
        self.input_gh = input_gh
        self.input_gd = input_gd
        self.input_temp = input_temp
        self.latitude = lat
        self.longitude = lon
        reference_angle = -175

        for angle_count in range(0, self.azimuthal_array_size + 1, 1):
            self.asimuth_angle[angle_count] = reference_angle
            reference_angle += 10

        for i in range(0, self.totalNumberOfHoursInYear, 1):
            # Declination (Climate file H6)
            self.declination[i] = 23.45 * np.sin((np.pi / 180) * math.floor(((284 + self.day) * 360) / 365))
            # B (Climate file I6)
            self.b[i] = (self.day - 1) * (360.0 / 365.0)

            # Tidsekvationen (Climate file J6)
            self.t_j[i] = 229.2 * (0.000075 + 0.001868 * np.cos((np.pi / 180) * self.b[i]) - 0.030277 * np.sin(
                (np.pi / 180) * self.b[i]) - 0.014615 * np.cos((np.pi / 180) * self.b[i] * 2) - 0.04089 * np.sin(
                (np.pi / 180) * self.b[i] * 2))

            # Sann soltid (Climate file K6)
            self.t_s[i] = (self.time_count * 60.0 + self.t_j[i] + (self.longitude - self.longitude_time_zone) * 4.0) / 60.0

            # Timvinkel omega (Climate file L2 )
            self.hour_angle[i] = 15 * (self.t_s[i] - 12)

            # Infallsvinkel (Calculations A6)
            self.inclination_angle[i] = np.arccos(
                np.sin((self.declination[i] * np.pi / 180)) * np.sin((self.latitude * np.pi / 180)) * np.cos(
                    (self.input_inclination * np.pi / 180)) - np.sin((self.declination[i] * np.pi / 180)) * np.cos(
                    (self.latitude * np.pi / 180)) * np.sin((self.input_inclination * np.pi / 180)) * np.cos(
                    (self.input_direction * np.pi / 180)) + np.cos((self.declination[i] * np.pi / 180)) * np.cos(
                    (self.latitude * np.pi / 180)) * np.cos((self.input_inclination * np.pi / 180)) * np.cos(
                    (self.hour_angle[i] * np.pi / 180)) + np.cos((self.declination[i] * np.pi / 180)) * np.sin(
                    (self.latitude * np.pi / 180)) * np.sin((self.input_inclination * np.pi / 180)) * np.cos(
                    (self.input_direction * np.pi / 180)) * np.cos((self.hour_angle[i] * np.pi / 180)) + np.cos(
                    (self.declination[i] * np.pi / 180)) * np.sin((self.input_inclination * np.pi / 180)) * np.sin(
                    (self.input_direction * np.pi / 180)) * np.sin((self.hour_angle[i] * np.pi / 180))) * (
                                           180 / np.pi)

            # Infalls-vinkel mindre än 90 grader, angle < 90 (Calculations B6)
            self.angle_below_90[i] = self.inclination_angle[i] if self.inclination_angle[i] < 90 else 90

            # (Calculations M6)
            self.solar_zenith_angle[i] = np.arccos(
                np.cos((self.latitude * np.pi / 180)) * np.cos((np.pi / 180) * self.declination[i]) * np.cos(
                    (np.pi / 180) * self.hour_angle[i]) + np.sin((np.pi / 180) * self.latitude) * np.sin(
                    (np.pi / 180) * self.declination[i])) * (180 / np.pi)

            # Geometri faktor för omräkning av direkt sol från horisontell yta till PV plan
            #  (Calculations C6)
            self.geometric_factor[i] = np.round(np.cos(self.angle_below_90[i] * (np.pi / 180)) / np.cos(np.minimum(
                87, self.solar_zenith_angle[i]) * np.pi / 180), 3)

            # Hay´s modell (Calculation R6)
            self.anisotropic_index[i] = np.round(self.hay_anisotropic * (self.input_gh[i] - self.input_gd[i]) / (1367 * np.cos(
                np.minimum(87, self.solar_zenith_angle[i]) * np.pi / 180)), 2)

            # Direkt solstråling i PV planet (Calculations D6 and climate file D6 -E6)
            self.direct_solar_angle[i] = (input_gh[i] - input_gd[i]) * self.geometric_factor[i] + self.anisotropic_index[i]                                     * self.input_gd[i] * self.geometric_factor[i]

            # Solhöjd relativt horiontalplanet as (Climate file N6)
            self.solar_altitude_angle[i] = np.arcsin(np.cos((self.latitude * np.pi / 180)) * np.cos(
                (np.pi / 180) * self.declination[i]) * np.cos(
                (np.pi / 180) * self.hour_angle[i]) + np.sin((np.pi / 180) * self.latitude) * np.sin(
                (np.pi / 180) * self.declination[i])) * (180 / np.pi)

            # Skugvinkel om flera PV rader (fast värde) (Calculations O6)
            shadow_angle_multiple_pv_rows = np.arctan(
                self.height_pv_module_out_with_glass * np.sin(self.input_inclination * np.pi / 180) / (
                        self.pv_row_spacing - self.height_pv_module_out_with_glass * np.cos(self.input_inclination
                                                                                  * np.pi / 180))) * 180 / np.pi

            # Diffus solstråling i PV planet (Calculations F6)
            self.diffuse_solar_radiation_pv_planet[i] = (self.input_gd[i] * (1 - self.anisotropic_index[i]) * ((1 + np.cos(
                (self.input_inclination + shadow_angle_multiple_pv_rows * self.correction_diffuse_shadowing)
                * np.pi / 180)) / 2) + self.input_gh[i] * self.ground_reflection_factor * ((1 - np.cos(
                (self.input_inclination - shadow_angle_multiple_pv_rows * self.correction_diffuse_shadowing)
                * np.pi / 180)) / 2))

            # Infallsvinkel beroende (Calculations I6)
            self.angle_of_attack[i] = 1 - math.pow((np.tan((self.inclination_angle[i] / 2) * (np.pi / 180))),
                                              self.angle_dependent_coefficient_direct_sunlight)
            # C3 (Climate file S6)
            self.c_3[i] = 1 if self.hour_angle[i] >= 0 else -1

            # The condition which is required to determine the value of C2
            c_2_factor = self.latitude - self.declination[i]

            # C2 (Climate file R6)
            self.c_2[i] = 1 if c_2_factor >= 0 else -1

            # Pseudo solar azimuth angle (Climate file T6)
            self.pseudo_solar_azimuth_angle[i] = np.arcsin(np.sin(self.hour_angle[i] * np.pi / 180) * np.cos(
                self.declination[i] * np.pi / 180) / np.sin(self.solar_zenith_angle[i] * np.pi / 180)) * 180 / np.pi

            # Hour angle-due east/west T (Climate file P6)
            num_a = np.tan(self.declination[i] * np.pi / 180)
            den_b = np.tan(self.latitude * np.pi / 180)
            """
            print('num_a -> ', num_a)
            print('den_b -> ', den_b)
            print('num_a / den_b -> ', (num_a / den_b))
            print('np.arccos(num_a / den_b ) -> ', np.arccos(num_a / den_b ))
            print('np.arccos(num_a / den_b ) * 180 / np.pi -> ', np.arccos(num_a / den_b ) * 180 / np.pi)
            print(' ----- '*3)
            """
            self.hour_angle_due[i] = np.arccos(num_a / den_b ) * 180 / np.pi

            # C1 (Climate files Q6)
            self.c_1[i] = 1 if np.abs(self.hour_angle[i]) <= self.hour_angle_due[i] else -1
            #print('c_1[i] -> ', c_1[i])

            # Solens azimutvinkel (räknat från söder) gs (Climate file U6)
            self.solar_azimuth_angle[i] = self.c_1[i] * self.c_2[i] * self.pseudo_solar_azimuth_angle[i] + self.c_3[i] * ((1 - self.c_1[i]
                                                                                                  * self.c_2[i]) / 2) * 180

            # Solhöjd över horisonten as (Climate file O6)
            self.solar_height_over_horizon[i] = self.solar_altitude_angle[i] if self.solar_altitude_angle[i] > 0 else 0

            # Solens skuggvinkel om systemet har flera rader (Solhöjd i söder) (Calculations P6)
            self.solar_shaded_angle_multiple_rows[i] = np.maximum(0.0001, np.arctan(
                np.tan(self.solar_height_over_horizon[i] * np.pi / 180) / np.cos(
                    (self.solar_azimuth_angle[i] - self.input_direction) * np.pi / 180)) * 180 / np.pi + 0.0001)

            # Andel fullt belyst PV yta (Calculations Q6)
            self.share_fully_illuminated_pv[i] = np.maximum(0, np.sin(
                self.solar_shaded_angle_multiple_rows[i] * np.pi / 180) / np.sin(
                (180 - self.solar_shaded_angle_multiple_rows[i] - self.input_inclination) * np.pi / 180) * (
                                                               self.height_pv_module_out_with_glass * np.sin(
                                                           self.input_inclination * np.pi / 180) / np.tan(
                                                           self.solar_shaded_angle_multiple_rows[i] * np.pi / 180)
                                                               + self.height_pv_module_out_with_glass * np.cos(
                                                           self.input_inclination * np.pi / 180)
                                                               - self.pv_row_spacing))

            # Korrektion för skuggning vid flera PV rader  (Calculations J6)
            self.correction_shaded_multiple_pv_rows[i] = ((self.number_of_rows_pv - 1) / self.number_of_rows_pv) * (
                    (self.height_pv_module_out_with_glass - self.share_fully_illuminated_pv[i]) /
                    self.height_pv_module_out_with_glass) + (1 / self.number_of_rows_pv)

            # Total oskoggad solstrålling i PV Planet (Calculations G6)
            self.total_unshaded[i] = self.direct_solar_angle[i] + self.diffuse_solar_radiation_pv_planet[i]

            # PV oskuggat (Calculations K6)
            self.output_pv_unshaded[i] = np.maximum(0, self.system_efficiency * (
                    self.direct_solar_angle[i] * self.input_efficiency * self.angle_of_attack[i]
                    * self.correction_shaded_multiple_pv_rows[i] + self.diffuse_solar_radiation_pv_planet[i]
                    * self.input_efficiency * self.k_diff) * (1 - self.alfa * (self.input_temp[i] + 1
                                                                / self.a1_heat_loss_figures_pv_modules
                                                                * (self.n0_thermal_solar_absorption_pv
                                                                   * self.total_unshaded[i]
                                                                   - self.input_efficiency
                                                                   * self.total_unshaded[i]) - 25)))


            # Testvinkel från Lookup (shading calculations L12)
            # This is a condition which is used to determine the value of test angle from lookup
            test_angle_lookup_condition = (5 + int((self.solar_azimuth_angle[i] / 10)) * 10)
            self.test_angle_from_lookup[i] = self.findIndex(self.asimuth_angle, test_angle_lookup_condition)
            if self.test_angle_from_lookup[i] == -1:
                self.test_angle_from_lookup[i] = self.shaded_angle[len(self.shaded_angle) - 1 if test_angle_lookup_condition > 175 else 0];
            else:
                self.test_angle_from_lookup[i] = self.shaded_angle[self.findIndex(self.asimuth_angle, test_angle_lookup_condition)]

            # Direkt solstrålning minus horistontavskärmning (Calculations E6)
            self.g_dir_shaded[i] = (0 if self.direct_solar_angle[i] < 0 else self.direct_solar_angle[i]) * (
                1 if self.solar_altitude_angle[i] > np.maximum(self.least_horizon_shielding,
                                                          self.test_angle_from_lookup[i]) else 0)

            # Total skoggad solstrålling i PV Planet (Calculations H6)
            self.total_shaded[i] = self.g_dir_shaded[i] + self.diffuse_solar_radiation_pv_planet[i]

            # PV skuggat (Calculations L6)
            self.output_pv_shaded[i] = np.maximum(0, self.system_efficiency * (
                    self.g_dir_shaded[i] * self.input_efficiency * self.angle_of_attack[i]
                    * self.correction_shaded_multiple_pv_rows[i] + self.diffuse_solar_radiation_pv_planet[i]
                    * self.input_efficiency * self.k_diff) * (1 - self.alfa * (self.input_temp[i]
                                                                + 1 / self.a1_heat_loss_figures_pv_modules
                                                                * (self.n0_thermal_solar_absorption_pv
                                                                   * self.total_shaded[i] - input_efficiency
                                                                   * self.total_shaded[i]) - 25)))

            self.day = self.day + 1 if (i + 1) % 24 == 0 else self.day
            self.time_count = 0.5 if self.time_count == 23.5 else self.time_count + 1

            i += 1
            
        # The below section is used for performing the per month solar calculations.
        for month_count in range(0, 12, 1):
            days = monthrange(self.current_year, month_count + 1)
            days_per_month = days[1]
            total_count_per_month = self.days_previous

            while total_count_per_month < self.days_previous + days_per_month * 24:
                self.sum_cal += self.output_pv_unshaded[total_count_per_month]
                self.sum_total += self.output_pv_unshaded[total_count_per_month]

                self.sum_total_unshaded += self.total_unshaded[total_count_per_month]
                self.sum_unshaded += self.total_unshaded[total_count_per_month]

                self.sum_s += self.output_pv_shaded[total_count_per_month]
                self.sum_total_s += self.output_pv_shaded[total_count_per_month]

                self.sum_shaded += self.total_shaded[total_count_per_month]
                self.sum_total_shaded += self.total_shaded[total_count_per_month]
                total_count_per_month += 1

            self.month_output_pv_unshaded[month_count] = self.sum_cal / 1000
            self.month_total_unshaded[month_count] = self.sum_total_unshaded / 1000
            self.month_output_pv_shaded[month_count] = self.sum_s / 1000
            self.month_total_shaded[month_count] = self.sum_total_shaded / 1000

            self.sum_cal = 0
            self.sum_total_unshaded = 0
            self.sum_s = 0
            self.sum_total_shaded = 0

            self.days_previous = total_count_per_month
            month_count += 1
            
        # Yearly Sum data
        self.sum_total = np.round((self.sum_total / 1000), 2)
        self.sum_unshaded = np.round((self.sum_unshaded / 1000), 2)
        self.sum_total_s = np.round((self.sum_total_s / 1000), 2)
        self.sum_shaded = np.round((self.sum_shaded / 1000), 2)
        #total_list = [sum_unshaded, sum_shaded, sum_total, sum_total_s]
        
        # Monthly Data
        monthSumOutputPvShadedList = np.round(self.month_output_pv_shaded  * self.area_module, 1)
        monthSumOutputPvUnshadedList = np.round(self.month_output_pv_unshaded * self.area_module, 1)
        monthSumTotalShadedList = np.round(self.month_total_shaded, 1)
        monthSumTotalUnshadedList = np.round(self.month_total_unshaded, 1)
        returnDict = {}
        monthlyData = {
            'monthSumOutputPvShadedList':{
                'data': monthSumOutputPvShadedList.tolist(),
                'total': round(sum(monthSumOutputPvShadedList), 1)
            },
            'monthSumOutputPvUnshadedList':{
                'data': monthSumOutputPvUnshadedList.tolist(),
                'total': round(sum(monthSumOutputPvUnshadedList), 1)
            },
            'monthSumTotalShadedList': {
                'data': monthSumTotalShadedList.tolist(),
                'total': round(sum(monthSumTotalShadedList), 1)
            },
            'monthSumTotalUnshadedList' : {
                'data': monthSumTotalUnshadedList.tolist(),
                'total': round(sum(monthSumTotalUnshadedList), 1)
            }
        }
        # Scatter Data
        scatterData = []
        for x, y in zip(self.total_shaded, (self.area_module * self.output_pv_shaded / 1000)):
            scatter = (x,y)
            scatterData.append([x, y])
        
        returnDict['monthlyData'] = monthlyData
        returnDict['scatterData'] = scatterData
        returnDict['yearlyData'] = self.get_yearly_data(self.current_year)
        return returnDict


# In[240]:


def write_json(data, fileName='postal_code_data.json'):
    f = open(fileName, 'w')
    json.dump(data, f, indent=2)
    f.close()
    return data

def open_data(d = 'postal_code_data.json'):
    f1 = open(d)
    dico = json.load(f1)
    f1.close()
    return dico


# In[241]:


postal_code_data = open_data('postal_code_data.json')
zones_data = open_data('zone_data.json')
filtered_zone = postal_code_data[str(postal_code_input)]
zone_data = zones_data[str(filtered_zone['zone'])]
input_gh = zone_data['gh']
input_gd = zone_data['gd']
input_temp = zone_data['temp']
lat = filtered_zone['coordinate'][0]
lon = filtered_zone['coordinate'][1]
print(filtered_zone)
print(lat, lon)


# In[242]:


solarCalculator = SolarCalculator(
    year= 2020,
    zipCode = 81470, 
    pmax = 1, 
    area_module = 6, 
    input_inclination=10, 
    input_direction = 0, 
    ground_reflection_factor = 0.2, 
    least_horizon_shielding = 10)
result = solarCalculator.compute(input_gh, input_gd, input_temp, lat, lon)
#result


# In[243]:


result


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




