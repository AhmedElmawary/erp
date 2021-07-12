'use strict'

function start() {
    let suplier_field  = document.getElementsByClassName('select2-selection select2-selection--single').item(1)
    let supplier_cash_element = document.getElementsByClassName('fieldBox field-supplier_cash_html').item(0)
    let transaction_type = document.getElementById('id_payment_type')
    let cash_after_transaction = document.getElementsByClassName('field-supplier_cash_after_transaction').item(0)
    let supplier_name =''
    let supplier_cash = ''
    let amount = document.getElementById('id_amount')
    let supplier_cash_html = ''
    let balance_after = 0

    if (!supplier_cash_element ) {
        return
    }

    if (!cash_after_transaction ) {
        return
    }
    
    let items_no = []
    
    if (! suplier_field ){ 
        return
    }
 
    supplier_cash_element.setAttribute('style', 'width: 800px')
    supplier_cash_element = supplier_cash_element.lastElementChild 
    supplier_cash_element.setAttribute('style', 'display: block; min-width: 200px; width: 100%;')
    cash_after_transaction = cash_after_transaction.lastElementChild.lastElementChild

    suplier_field.addEventListener('mouseup', function() {
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
                    cash_after_transaction.innerText = parse_to_number(parseInt(supplier_cash)  - parseInt(amount.value)) 
                } else {
                    cash_after_transaction.innerText = parse_to_number(parseInt(supplier_cash)  + parseInt(amount.value))
                }
            }
        }
            
        for (let item of items_no) {
            item.addEventListener('mousedown', function () {
                supplier_name = item.innerText
                let  ajax = new XMLHttpRequest()
                let replace_with = 'supplier/'
                let controller_cash_url = window.location.href.replace(/add.*/,replace_with +  supplier_name)
                ajax.open('GET', controller_cash_url)
                ajax.onload = function() {
                    if (ajax.status == 200) {
                        supplier_cash = JSON.parse(ajax.responseText)
                        if (supplier_cash) {
                            // supplier_cash_html = supplier_cash['cash_html']
                            supplier_cash = supplier_cash['cash']
                        supplier_cash_element.setAttribute('style', "font-size: 18px; width: 360px")
                        supplier_cash_element.innerText =  supplier_cash 
                 
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


