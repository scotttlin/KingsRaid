import sys

import os
import nox
import Common

def gen_raid():
    Common.confirm(start_condition='The macro can be started in a raid lobby or while a raid is in progress.')

    nox.click_button('start_raid', 5000)
    nox.click_button('confirm_insufficient_members', 500)
    nox.click_button('abandon_raid', 5000)
        
def gen_raid_leader():
    Common.confirm(start_condition='The macro can be started in a raid lobby or while a raid is in progress.')

    for i in range(0, 10):
        nox.click_button('start_raid', 300)
    nox.click_button('confirm_insufficient_members', 500)
    nox.click_button('abandon_raid', 5000)

def gen_raid_experimental():

    Common.confirm()
    nox.click_button('start_raid', 10000)
    nox.click_button('stam_potion_confirm', 1000)
    nox.click_button('abandon_raid', 1000)
