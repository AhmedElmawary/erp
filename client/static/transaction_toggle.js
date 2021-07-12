'use static'
function start_toggle() {
	let transaction_type  =  document.getElementById('id_payment_type');
	if (! transaction_type) {
		return
	}
	transaction_type.addEventListener('change', function () {
		value_transaction =transaction_type.value
		
		if  (! value_transaction) {
			value_transaction = 1
		}

		document.cookie = 'value_transaction='+ value_transaction +';'
		window.location.reload()
	});

	if (document.cookie.match('value_transaction')) {
		let array_of_cookies = document.cookie.split('=')
		let value_to_attach = array_of_cookies[array_of_cookies.length -1]
		transaction_type.value = value_to_attach
	}

}
window.addEventListener('load', start_js) 
