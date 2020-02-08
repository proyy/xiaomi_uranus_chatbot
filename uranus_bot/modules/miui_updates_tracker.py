#!/usr/bin/env python3.7
"""MIUI Updates Tracker commands"""
from uuid import uuid4

from requests import get
import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,\
    InlineQueryResultArticle, InputTextMessageContent, ParseMode

from uranus_bot.modules.mwt import MWT
from uranus_bot.modules.extras import check_codename, set_branch, set_region

DEVICES = yaml.load(get(
    "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
    "xiaomifirmwareupdater.github.io/master/" +
    "data/miui_devices.yml").text, Loader=yaml.CLoader)
SITE = 'https://xiaomifirmwareupdater.com'


@MWT(timeout=60 * 60)
def load_fastboot_data(device):
    """
    load latest fasboot ROMs data form MIUI tracker yaml files
    :argument device - Xiaomi device codename
    :returns data - a list with merged stable, weekly, current, and EOL data
    """
    stable_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/" +
        "stable_fastboot/stable_fastboot.yml").text, Loader=yaml.CLoader)
    weekly_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/" +
        "weekly_fastboot/weekly_fastboot.yml").text, Loader=yaml.CLoader)
    eol_stable_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/EOL/" +
        "stable_fastboot/stable_fastboot.yml").text, Loader=yaml.CLoader)
    eol_weekly_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/EOL/" +
        "weekly_fastboot/weekly_fastboot.yml").text, Loader=yaml.CLoader)
    latest_stable = [i for i in stable_roms
                     if device == i['codename'].split('_')[0] and i['version']]
    latest_weekly = [i for i in weekly_roms
                     if device == i['codename'].split('_')[0] and i['version']]
    eol_stable = [i for i in eol_stable_roms
                  if device == i['codename'].split('_')[0] and i['version']]
    eol_weekly = [i for i in eol_weekly_roms
                  if device == i['codename'].split('_')[0] and i['version']]
    data = latest_stable + latest_weekly + eol_stable + eol_weekly
    return data


@MWT(timeout=60 * 60)
def load_recovery_data(device):
    """
    load latest recovery ROMs data form MIUI tracker yaml files
    :argument device - Xiaomi device codename
    :returns data - a list with merged stable, weekly, current, and EOL data
    """
    stable_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/" +
        "stable_recovery/stable_recovery.yml").text, Loader=yaml.CLoader)
    weekly_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "xiaomifirmwareupdater.github.io/master/" +
        "data/devices/miui11.yml").text, Loader=yaml.CLoader)
    eol_stable_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/EOL/" +
        "stable_recovery/stable_recovery.yml").text, Loader=yaml.CLoader)
    eol_weekly_roms = yaml.load(get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/"
        "miui-updates-tracker/master/EOL/" +
        "weekly_recovery/weekly_recovery.yml").text, Loader=yaml.CLoader)
    stable_roms = [i for i in stable_roms
                   if device == i['codename'].split('_')[0] and i['version']]
    try:
        weekly_roms = [i for i in weekly_roms
                       if device == i['codename'].split('_')[0] and i['version']][0]
    except IndexError:
        weekly_roms = {}
    eol_stable_roms = [i for i in eol_stable_roms
                       if device == i['codename'].split('_')[0] and i['version']]
    eol_weekly_roms = [i for i in eol_weekly_roms
                       if device == i['codename'].split('_')[0] and i['version']]
    data = stable_roms + eol_stable_roms + eol_weekly_roms
    if weekly_roms:
        data += [weekly_roms]
    return data


@check_codename(markup=True)
def fetch_recovery(device, inline=False):
    """
    fetch latest recovery ROMs for a device from MIUI updates tracker yaml files
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    """
    data = load_recovery_data(device)
    keyboard = []
    if not data:
        return ""
    name = DEVICES[device]
    message = f"*Latest {name} MIUI Official Recovery ROMs*"
    for i in data:
        version = i['version']
        android = i['android']
        download = i['download']
        region = set_region(download.split('/')[-1], version)
        keyboard.append([InlineKeyboardButton(f"{region} {version} | "
                                              f"{android}", f"{download}")])
    keyboard.append([InlineKeyboardButton("ROMs Archive",
                                          f"{SITE}/archive/miui/{device}/"),
                     InlineKeyboardButton("MIUIUpdatesTracker",
                                          url="https://t.me/MIUIUpdatesTracker")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if inline:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title=f"Search {device} recovery ROM downloads",
            input_message_content=InputTextMessageContent(
                message, parse_mode=ParseMode.MARKDOWN), reply_markup=reply_markup)]
        return results
    return message, reply_markup


@check_codename(markup=True)
def fetch_fastboot(device, inline=False):
    """
    fetch latest fastboot ROMs for a device from MIUI updates tracker yaml files
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    """
    keyboard = []
    data = load_fastboot_data(device)
    if not data:
        return ""
    name = DEVICES[device]
    message = f"*Latest {name} MIUI Official Fastboot ROMs*"
    for i in data:
        version = i['version']
        android = i['android']
        download = i['download']
        region = set_region(download.split('/')[-1], version)
        keyboard.append([InlineKeyboardButton(f"{region} {version} | {android}", f"{download}")])
    keyboard.append([InlineKeyboardButton("ROMs Archive", f"{SITE}/archive/miui/{device}/"),
                     InlineKeyboardButton("MIUIUpdatesTracker",
                                          url="https://t.me/MIUIUpdatesTracker")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if inline:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title=f"Search {device} fastboot ROM downloads",
            input_message_content=InputTextMessageContent(
                message, parse_mode=ParseMode.MARKDOWN), reply_markup=reply_markup)]
        return results
    return message, reply_markup


@check_codename(markup=False)
def check_latest(device, inline=False):
    """
    check latest version of ROMs for a device from MIUI updates tracker yaml files
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    """
    data = load_fastboot_data(device)
    if not data:
        return ""
    name = DEVICES[device]
    message = f"*Latest MIUI Versions for {name}*:\n"
    for i in data:
        version = i['version']
        rom_type = set_branch(version)
        file = i['filename']
        region = set_region(file, version)
        message += f"{region} {rom_type}: `{version}`\n"
    if inline:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title=f"Search {device} latest MIUI versions",
            input_message_content=InputTextMessageContent(
                message, parse_mode=ParseMode.MARKDOWN))]
        return results
    return message


@check_codename(markup=True)
def history(device, inline=False):
    """
    generate latest firmware links for a device
    :argument device - Xiaomi device codename
    :returns message - telegram message string
    """
    message = f"*MIUI ROMs archive for {DEVICES[device]}* (`{device}`)"
    archive = InlineKeyboardButton(f"ROMs Archive", f"{SITE}/archive/miui/{device}/")
    channel = InlineKeyboardButton("MIUIUpdatesTracker", url="https://t.me/MIUIUpdatesTracker")
    reply_markup = InlineKeyboardMarkup([[archive, channel]])
    if inline:
        results = [InlineQueryResultArticle(
            id=uuid4(),
            title=f"Search {device} Official ROMs archive",
            input_message_content=InputTextMessageContent(
                message, parse_mode=ParseMode.MARKDOWN), reply_markup=reply_markup)]
        return results
    return message, reply_markup