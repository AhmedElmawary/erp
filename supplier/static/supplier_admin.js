'use strict'

function start_js() {
    let path =  window.location.pathname.split('/')
    path.pop()
    if (path.pop() == 'supplier') {
        let transactions_to = document.getElementsByClassName('transaction_date_to')
        // let transactions_from = document.getElementsByClassName('transaction_date_from')
        let today =  new Date()
        today = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate()

     
        for (let row of  transactions_to) {
            row.addEventListener('change', function() {
                let transaction_from_str = row.getAttribute('id').replace('to', 'from')
                let transaction_from = document.getElementById(transaction_from_str)
                
                let transaction_from_value = transaction_from.value
                if  (! transaction_from.value ) {
                    transaction_from.value  = today
                    transaction_from_value = today
                }   
                let supplier_id = row.getAttribute('data-inside')
                document.cookie = 'transaction_from=' +  transaction_from_value  +";"
                document.cookie = 'transaction_to=' +  row.value +';'
                
                window.location.replace(supplier_id+'/supplier_transactions')
            })
        }
        return
    }
    
    let cash = document.getElementById('id_cash')
    let credit = document.getElementsByClassName('field-get_credit').item(0).lastElementChild.lastElementChild
    let debit = document.getElementsByClassName('field-get_debit').item(0).lastElementChild.lastElementChild
    let net = document.getElementsByClassName('field-get_net').item(0).lastElementChild.lastElementChild
    
    function change_color() {
        cash.style.color = 'black'
        if (cash.value < 0 ) {
            cash.style.color = 'green'
        } else if (cash.value > 0) {
            cash.style.color = 'red'
        }
    }
    
    function change_readonly_color(element) {
        element.style.color = 'black'
        if (parseFloat(element.innerText) > 0) {         
            element.style.color = 'red'
        }else if (parseFloat(element.innerText) <0){
            element.style.color = 'green'
        }
    }

    function change_debit_color() {
        debit.style.color = 'red'
    }

    function change_credit_color() {
        credit.style.color = 'green'
    }

    function dynamic_readonly_color() {
        change_readonly_color(net)
        change_debit_color()
        change_credit_color()
    }

    function change_cash_color() {
        cash.style.color = 'black'
        if (cash.value < 0 ) {
            cash.style.color = 'green'
        } else if (cash.value > 0) {
            cash.style.color = 'red'
        }
    }
    
    function dynamic_colors() {
        change_cash_color()
        dynamic_readonly_color()
        cash.addEventListener('change', change_cash_color)
    }

    dynamic_colors()
}



window.addEventListener('load', start_js) 
