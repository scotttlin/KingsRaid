import nox
import Common

# reduce the time for easier conquests.  This assumes we're starting at ch7.  If we support less than all chapters then this will need to be adjusted.
def get_conquest_run_time(conquest_chapter, longest_run_time):
	run_time = longest_run_time

	if conquest_chapter == "ch2_conquest":
		run_time = longest_run_time - 35
	elif conquest_chapter == "ch3_conquest":
		run_time = longest_run_time - 30
	elif conquest_chapter == 'ch4_conquest':
		run_time = longest_run_time - 25
	elif conquest_chapter == 'ch5_conquest':
		run_time = longest_run_time - 20
	elif conquest_chapter == 'ch6_conquest':
		run_time = longest_run_time - 15
	elif conquest_chapter == 'ch7_conquest':
		run_time = longest_run_time

	# establish a minimum
	if run_time >= 45:
		return run_time
	else:
		return longest_run_time

# auto conquest on one chapter
# Protection is in place if you have used up your keys.  This will then effectively click "open" and "x out" over and over, without clicking reset until the macro completes.
def gen_single_conquest(conquest_chapter, longest_run_time):

	nox.click_button('portal', 2000)
	nox.click_button('conquests', 2000)
	nox.click_button(conquest_chapter, 2000)
	nox.click_button('move_to_conquest', 5000)  # map render delay
	nox.click_button('prepare_battle', 2000)
	nox.click_button('get_ready_for_battle', 2000)
	nox.click_button('auto_repeat', 2000)
	nox.click_button('repeat_ok', (get_conquest_run_time(conquest_chapter, longest_run_time) * 1000 * 5))  # for now this will be 60s per run or 5 min total.  We can make this smarter later.
	nox.click_button('insufficient_keys', 2000)
	nox.click_button('x_out', 1000)
	nox.click_button('x_out', 1000) # second x_out in case of key reset
	nox.click_button('exit_conquest', 20000) # long render
		
# Current runtime is 34.76 minutes.  In the future we'll allow the user to adjust their ch7 runtime.  Then scale off that for easier runs.
# On a slower (cpu) laptop, the quickest one run can be is around 40s.  This starts with 90s per run.
# Currently designed to work with chapters 2-7, not a partial of that.  Currently expects all keys available and no additional keys.
def gen_conquest():

	longest_run_time = nox.prompt_user_for_int('Enter longest ch7 run (default is 90s): ', default = 90)   
	# longest_ch7_runtime = nox.prompt_user_for_int('Enter longest ch7 run (default is 90s): ', default = 90)	  
	# # longest_non-ch7_runtime = nox.prompt_user_for_int('Enter longest non-ch7 run (default is 45s): ', default = 45)


	gen_single_conquest('ch2_conquest', get_conquest_run_time('ch2_conquest', longest_run_time))
	gen_single_conquest('ch3_conquest', get_conquest_run_time('ch3_conquest', longest_run_time))
	gen_single_conquest('ch4_conquest', get_conquest_run_time('ch4_conquest', longest_run_time))
	gen_single_conquest('ch5_conquest', get_conquest_run_time('ch5_conquest', longest_run_time))
	gen_single_conquest('ch6_conquest', get_conquest_run_time('ch6_conquest', longest_run_time))
	gen_single_conquest('ch7_conquest', get_conquest_run_time('ch7_conquest', longest_run_time))

	Common.confirm(start_condition='The macro should be started only when the Portal button is visible')
