'use strict'

function start_js() {
    let  btns = document.getElementsByClassName('account_statment_btn')
    let  inputs_date_from = document.getElementsByClassName('account_statment_from')
    let  inputs_date_to = document.getElementsByClassName('account_statment_to')
    let href = 0

    if (! btns) {
        return
    }

    for (let index=0; index< inputs_date_to.length; index++) {
        inputs_date_to.item(index).addEventListener('change', function() {
            href = btns.item(index).href.split('/')
            href[8] = inputs_date_from.item(index).value
            href[9] = inputs_date_to.item(index).value
            btns.item(index).setAttribute('href', href.join('/'))
        })
    }

    for (let index=0; index< inputs_date_from.length; index++) {
        inputs_date_from.item(index).addEventListener('change', function() {
            href = btns.item(index).href.split('/')
            href[8] = inputs_date_from.item(index).value
            href[9] = inputs_date_to.item(index).value
            btns.item(index).setAttribute('href', href.join('/'))
        })
    }
    for (let index=0; index< inputs_date_from.length; index++) {
        btns.item(index).addEventListener('click', function(event){
        event.preventDefault();
        window.open(btns.item(index).href,"print","toolbar=no,scrollbars=yes,resizable=0,top=100,left=100,width=595,height=842")
    });
}
}


window.addEventListener('load', start_js) 
