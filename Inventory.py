import sys

import os
import nox

def grind_or_sell_all(is_grind):
	# Grind
	button = 'grind' if is_grind else 'sell'

	nox.click_button(button, 3500)

	# Grind all
	nox.click_button('grind_all', 3500)

	# Click the Grind button on the window that pops up
	nox.click_button('grind_2', 3500)

	# Confirmation
	nox.click_button('grind_confirm', 3500)

	if is_grind:
		# Click on the screen to get rid of the results
		nox.click_button('dismiss_results', 3500)

def manage_inventory(should_grind, should_sell):
	if should_grind:
		grind_or_sell_all(True)
	if should_sell:
		grind_or_sell_all(False)
