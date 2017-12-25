rule_sets = {
	'nick_test_1': {  # Buying / selling happens when conditions are met and the resulting action wouldn't violate a limit
		'buy': [  # Each element specifies a set of conditions that may trigger the action
			[  # Each dict specifies a condition. All conditions within the element must be met to trigger the action
				{
					'indicator': 'sma',
					'direction': 'up',
					'steepness': 0.4,
					'over_n_steps': 10
				}
			]
		],
		'sell': [
			[
				{
					'indicator': 'sma',
					'direction': 'down',
					'steepness': 0.4,
					'over_n_steps': 10
				}
			]
		],
		'limits': {
			'n_positions': 1,
		},
		'profit_scraping': {}
	}
}