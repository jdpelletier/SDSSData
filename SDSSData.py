
from datetime import datetime, timedelta
import sys

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, errors, get_sun, get_moon


class SDSSData(object):
    def __init__(self, filename, location):
        self.hdu_list = fits.open(filename)
        self.hdr = self.hdu_list[0].header
        self.ra = self.hdr['RA']
        self.dec = self.hdr['DEC']
        try:
            self.location = EarthLocation.of_site(location)
        except errors.UnknownSiteException:
            print('Unknown site, use one of these sites:')
            print(EarthLocation.get_site_names())
            sys.exit(1)

    def convert_coordinates(self):
        return SkyCoord(self.ra, self.dec, unit='deg')

    def time_now(self):
        return Time(datetime.utcnow())

    def alt_az(self):
        altAz = self.convert_coordinates().transform_to(AltAz(obstime=self.time_now(),location=self.location))
        star_alt = altAz.alt.value
        star_az = altAz.az.value
        return star_alt, star_az

    def is_up(self):
        star_alt, star_az = self.alt_az()
        if star_alt > 32.8:
            return str(f"El {star_alt:.2f}, Az {star_az:.2f}        STAR IS UP!")
        else:
            return str(f"El {star_alt:.2f}, Az {star_az:.2f}")

    def displayCoordinates(self):
        return self.convert_coordinates().to_string('hmsdms', sep = ':')

    def plot_star(self):
        plt.figure()
        tomorrow = Time(datetime.now()) + timedelta(1)
        midnight = Time(datetime(year=tomorrow.value.year, month=tomorrow.value.month,
                        day=tomorrow.value.day, hour=10, minute=0, second=0))
        delta_midnight = np.linspace(-12, 12, 1000)*u.hour
        times_tonight = midnight + delta_midnight
        frame_tonight = AltAz(obstime=times_tonight, location=self.location)
        sunaltazs_tonight = get_sun(times_tonight).transform_to(frame_tonight)
        moon_tonight = get_moon(times_tonight)
        moonaltazs_tonight= moon_tonight.transform_to(frame_tonight)
        targetaltaz_tonight = self.convert_coordinates().transform_to(frame_tonight)

        plt.plot(delta_midnight, sunaltazs_tonight.alt, color='r', label='Sun')
        plt.plot(delta_midnight, moonaltazs_tonight.alt, color=[0.75]*3, ls='--', label='Moon')
        plt.scatter(delta_midnight, targetaltaz_tonight.alt,
                c=targetaltaz_tonight.az, label=self.hdr['NAME'], lw=0, s=8,
                cmap='viridis')
        plt.fill_between(delta_midnight.to('hr').value, 0, 90,
                sunaltazs_tonight.alt < -0*u.deg, color='0.5', zorder=0)
        plt.fill_between(delta_midnight.to('hr').value, 0, 90,
                sunaltazs_tonight.alt < -18*u.deg, color='k', zorder=0)
        plt.colorbar().set_label('Azimuth [deg]')
        plt.legend(loc='upper left')
        plt.xlim(-12, 12)
        plt.xticks(np.arange(13)*2 -12)
        plt.ylim(0, 90)
        plt.title('Star ALT/AZ for the night')
        plt.xlabel('Hours from Midnight')
        plt.ylabel('Altitude [deg]')
        plt.show()



    def close_fits_file(self):
        self.hdu_list.close()
