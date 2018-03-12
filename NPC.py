import sys

import os
import nox
import Common
import Inventory

# this is likely obsolete.
def gen_grindhouse():
	# The generated macro assumes you are on the Buy screen, Tier 3 is already selected, and an item is
	# highlighted.
	print()
	items_to_buy = nox.prompt_user_for_int(
		"How many items should be purchased each cycle?\n"
		"If you don't have at least this much inventory space the macro will de-sync.\n"
		"Number of items to purchase: ")

	print()
	buy_delay = nox.prompt_user_for_int("Enter the number of milliseconds between each click while purchasing\n"
										"items.  A lower number will make the macro run faster, but could cause\n"
										"the macro to get out of sync on slower machines.  If the macro doesn't\n"
										"register clicks properly while buying items, run the generator again\n"
										"and choose a higher number until you find what works.\n\n"
										"Milliseconds (Default=325): ", default=325)

	Common.confirm(properties={'Items to buy' : items_to_buy, 'Delay' : buy_delay },
			start_condition='The macro should be started from the forge shop.')

	# Click on first item in forge shop
	nox.click_button('forge_first_item', 1500)

	# Buy 300 items
	for i in range(0, items_to_buy):
		nox.click_button('buy', buy_delay)
		
	# Exit twice (to Orvel map)
	nox.click_button('exit', 1500)
	nox.click_button('exit', 1500)

	# Open inventory
	nox.click_button('inventory', 1500)

	Inventory.grind_or_sell_all(True)

	# Exit back to Orvel world map
	nox.click_button('exit', 1500)

	# Re-enter the shop.  Delay set to 2500 here since there's an animated transition
	# that takes a little extra time
	nox.click_button('enter_node', 5000)

	# Click Use Shop button
	nox.click_button('use_shop', 1500)
