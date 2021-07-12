'use static'
function start_toggle() {
	let transaction_type  =  document.getElementById('id_payment_type');
	// let amount  =  document.getElementById('id_amount');
	// let amount_value_palce = ''
	let cookies = document.cookie.split(';')
	let  transaction_supplier_value_palce =''
	if (! transaction_type) {
		return
	}

	transaction_type.addEventListener('change', function () {
	let value_transaction = transaction_type.value
	document.cookie = 'value_transaction_supplier='+ value_transaction +';'
	// document.cookie = 'amount_value='+ amount.value +';'

	transaction_type.value = value_transaction 

		window.location.reload()
	});

	// for (let cookie of cookies) {
	// 	if (cookie.indexOf('amount_value=') >= 0) {
	// 		amount_value_palce = cookie.split('=')[1]
	// 		amount.value = amount_value_palce
	// 		document.cookie = 'amount_value='+ amount_value_palce +';'
	// 		break
	// 	}
	// }

	for (let cookie of cookies) {
		if (cookie.indexOf('value_transaction_supplier=') >= 0) {
			transaction_supplier_value_palce = cookie.split('=')[1]
			document.cookie = 'transaction_supplier_value='+ transaction_supplier_value_palce +';'
			transaction_type.value = parseInt(transaction_supplier_value_palce)
			break
		}
	}
	

}
window.addEventListener('load',start_toggle )