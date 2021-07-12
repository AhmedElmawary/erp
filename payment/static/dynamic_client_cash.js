'use strict'

function start() {
    let client_field  = document.getElementsByClassName('select2-selection select2-selection--single').item(1)
    let client_cash_element = document.getElementsByClassName('field-client_cash_html').item(0)
    let transaction_type = document.getElementById('id_payment_type')
    let cash_after_transaction = document.getElementsByClassName('field-client_cash_after_transaction').item(0)
    let cash_after_transaction_str = document.getElementById('cash_after_str')
    let client_name =''
    let client_cash = ''
    let amount = document.getElementById('id_amount')
    let client_cash_html = ''
    let client_cash_new = 0
    let csrf = document.getElementsByName('csrfmiddlewaretoken').item(0).value

    if (!client_cash_element ) {
        return
    }

    if (!cash_after_transaction ) {
        return
    }
    
    let items_no = []
    
    if (! client_field ){ 
        return
    }
 

    client_cash_element = client_cash_element.lastElementChild 
    
    cash_after_transaction.setAttribute('style', "font-size: 18px")
    cash_after_transaction = cash_after_transaction.lastElementChild.lastElementChild
    client_field.addEventListener('mouseup', function() {
        let select_options = document.getElementsByClassName('select2-results__options').item(0);
        if (select_options){ 
             items_no = select_options.children

        }

        function parse_to_number(number) {
            return Number(number).toFixed(2)
        }
    
        function calculate_cashes() {
            if  (parseInt(amount.value)) {
                if (transaction_type.value == 2) {
                    client_cash_new = parse_to_number(parseInt(client_cash)  - parseInt(amount.value)) 
                } else {
                    client_cash_new = parse_to_number(parseInt(client_cash)  + parseInt(amount.value))
                }
                cash_after_transaction.innerText = client_cash_new 
                let  cash_to_str_url = location.href.replace('/add/', '/amount_to_string')
                // let client_new_cash_str = new XMLHttpRequest()
                // client_new_cash_str.open('POST', cash_to_str_url)
                // client_new_cash_str.setRequestHeader('X-CSRFToken', csrf)
                // client_new_cash_str.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                // client_new_cash_str.onload = function() {
                //     if (client_new_cash_str.status == 200) {
                //         client_new_cash_str = JSON.parse(client_new_cash_str.responseText)['str'] 
                //         cash_after_transaction_str.innerText =  client_new_cash_str
                //     }

                }
                // client_new_cash_str.send('amount='+ client_cash_new )
            // }
        }
            
        for (let item of items_no) {
            item.addEventListener('mousedown', function () {
                client_name = item.innerText
                let  ajax = new XMLHttpRequest()
                let controller_cash_url = window.location.href.replace('/add/','/client/'+client_name)

                ajax.open('GET', controller_cash_url)
                ajax.onload = function() {

                    if (ajax.status == 200) {

                        client_cash = JSON.parse(ajax.responseText)
                        if (client_cash) {
                            // client_cash_html = client_cash['cash_html']
                            client_cash = client_cash['cash']
                        client_cash_element.setAttribute('style', "font-size: 18px; width: 360px")
                        client_cash_element.lastElementChild.innerText =  client_cash 
                 
                       }
                    calculate_cashes()
                    }
                }
                ajax.send()
            });
        }

        amount.addEventListener('change', calculate_cashes)
    });
}

window.addEventListener('load', start) 


