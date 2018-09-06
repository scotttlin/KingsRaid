import sys

import os
import nox
import Common
import Inventory


def prompt_inventory_management_properties():
	choice = nox.prompt_choices(
		'Should I (G)rind All or (S)ell All?', ['G', 'S'])

	if choice.lower() == 'g':
		return (True, False)

	return (False, True)
def do_generate_inventory_management_for_adventure(should_grind, should_sell):
	# At this point we're at the victory screen.  We need to click the Inventory button on the
	# left side.  This involves a loading screen and can take quite some time, so wait 15 seconds.
	nox.click_loc((80, 230), 25000)

	Inventory.manage_inventory(should_grind, should_sell)

	# Exit back to Orvel map
	nox.click_button('exit', 3500)
def gen_natural_stamina_farm():
	print()
	use_pot = nox.prompt_user_yes_no(
		"Should the macro automatically use a stamina potion when you run out?")

	inventory_management = nox.prompt_user_for_int(
		"Enter the frequency (in minutes) at which to manage inventory.\n"
		"To disable inventory management, press Enter without entering a value: ", min=1,
		default = -1)

	inv_management_sync = None
	properties={'Use Potion': use_pot}

	notes = []
	if inventory_management != -1:
		inv_management_sync = nox.prompt_user_for_int(
			'Enter the maximum amount of time (in whole numbers of minutes) it takes your team\n'
			'to complete a story dungeon.  (Default = 3): ', default = 3)
		(should_grind, should_sell) = prompt_inventory_management_properties()
		properties['Inventory Management Sync Time'] = '{0} minutes'.format(inv_management_sync)
		s = None
		if should_grind and should_sell:
			s = "Sell then grind"
		elif should_grind:
			s = "Grind"
		else:
			s = "Sell"
		properties['Manage Inventory'] = '{0} every {1} minutes'.format(s, inventory_management)
		notes=['When the macro is getting ready to transition to the inventory management\n'
				'	  phase, it may appear the macro is stuck doing nothing on the victory screen.\n'
				'	  This is intentional, and it can take up to {0} minutes before the transition\n'
				'	  to the inventory screen happens.'.format(inv_management_sync)]
	else:
		properties['Manage Inventory'] = 'Never'

	Common.confirm(
		properties=properties,
		start_condition='The macro should be started while a battle is in progress.',
		notes=notes)

	def generate_one_click_cycle():
		# No effect during battle or on victory screen, but if we get stuck in Get Ready
		# for Battle screen after inventory management, this starts us again.  Make sure
		# to do this BEFORE the continue button, otherwise the continue button will click
		# one of our heroes and remove them from the lineup.  By putting this click first
		# it guarantees that we either enter the battle, or get the stamina window (in
		# which case the click doesn't go through to the button underneath).
		nox.click_button('start_adventure', 500)

		# Be careful with the x coordinate here so that it clicks in between items in the
		# inventory if your inventory is full.
		nox.click_loc((503, 352), 500)	  # Continue (game pauses sometimes mid-battle)

		nox.click_loc((1204, 494), 500)	 # Retry
		nox.click_loc((572, 521), 500)	  # Single Repeat button.  Careful not to click the button that
											# edits the count of stamina potions to use.
		if use_pot:
			nox.click_loc((759, 558), 500)	  # Stamina Potion OK
		else:
			nox.click_loc((940, 190), 500)	  # Close stamina pop-up

	if inventory_management == -1:
		# If we don't need to manage inventory, just generate a simple macro that can loop forever.
		generate_one_click_cycle()
	else:
		# If we do need to manage inventory, then first generate enough cycles of the normal story
		# repeat to fill up the entire specified number of minutes.
		nox.repeat_generator_for(generate_one_click_cycle, inventory_management * 60)

		# Then switch to a mode where we just try to get to the victory screen but not initiate a
		# repeat.  We do this by just clicking the continue button every second for 2 minutes.
		# Hopefully 3 minutes is enough to finish any story level.
		def get_to_victory_screen():
			# Continue (game pauses sometimes mid-battle)
			nox.click_loc((503, 352), 1000)

			# Need to make sure to click below the loot results so they get dismissed properly
			nox.click_loc((503, 500), 1000)

		nox.repeat_generator_for(get_to_victory_screen, inv_management_sync * 60)

		# At this point the Inventory button on the top left side of the victory should be clickable.
		# so initiate the process of clicking, grinding/selling, and getting back into the battle.
		do_generate_inventory_management_for_adventure(should_grind, should_sell)

		# Re-enter the battle from the world map, using a potion if necessary
		re_enter_adventure(use_pot)

def re_enter_adventure(use_potion):
	# Re-enter the map.  Since there's a loading transition, this takes a little extra time.
	nox.click_button('enter_node', 3500)

	# Prepare battle -> start adventure.
	nox.click_button('start_adventure', 3500)
	nox.click_button('start_adventure', 3500)

	# The stamina window may have popped up.  Use a potion
	if use_potion:
		nox.click_loc((759, 558), 2000)	  # Stamina Potion OK
