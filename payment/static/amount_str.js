'use strict'

function start() {
    let amount = document.getElementById('id_amount')
    let str_ammount_holder = document.getElementsByClassName('fieldBox field-str_amount').item(0)

    if (str_ammount_holder){
        str_ammount_holder.style.width = '800px'

    }

    if (! amount) {
        return
    }
    function process_amount_to_str() {
        let ajax  = new XMLHttpRequest()
        let csrf = document.getElementsByName('csrfmiddlewaretoken').item(0).value
        let url = location.href.replace(/add.*/, 'amount_to_string')
        let str_amount = document.getElementById('str_amount')

        if (!amount.value) {
            amount.value = 0
        }
        ajax.open('POST', url)
        
        ajax.setRequestHeader('X-CSRFToken', csrf)
        // ajax.setRequestHeader('Content-type', 'application/json');
        ajax.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

        ajax.onload = function () {
            if (ajax.status == 200) {
                let amount_str = JSON.parse(ajax.responseText)['str'] 
                str_amount.innerText=amount_str
            }
        }
        
        // let json_ = JSON.stringify({"amount": "15"})
        ajax.send("amount="+amount.value)
}
    amount.addEventListener('keyup', process_amount_to_str)
}

window.addEventListener('load', start)
