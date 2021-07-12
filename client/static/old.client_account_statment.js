'use strict'

function start_js() {
    let  btn = document.getElementById('account_statment_btn')
    let  date_to = document.getElementById('account_statment_to')
    let date_from  = document.getElementById('account_statment_from')
    let csrf  = document.getElementsByName('csrfmiddlewaretoken').item(0).value
    let cuurnet_date =  new Date()
    let modifed_month = cuurnet_date.getMonth()+1
    let month = cuurnet_date.getMonth() < 10 ?  '0'+modifed_month : modifed_month 
    let this_month =  cuurnet_date.getFullYear() +'-'+    month
    let today = this_month +'-'+ cuurnet_date.getDate()
    let start_day = this_month + '-'  + '01'

    if (! date_from){
        return
    }
    function set_default_date(){
        date_from.setAttribute('max', today)
        date_from.value = start_day 
        date_to.setAttribute('min', start_day)
        date_to.value = today 
    }
    
    function default_date_value(){
       return start_day + '/'+ today 
    }

    function gather_client_ids () {
        let results = document.evaluate( "//tr[@class='selected']//input[@name='_selected_action']", document,null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null );
        let iterator  = results.iterateNext()
        let clients_ids =[]    
        let clients_query_str = ''
        while(iterator){
            clients_query_str+= iterator.value +":"
            iterator  = results.iterateNext()
        }
        let index = clients_query_str.lastIndexOf('&')
        clients_query_str= clients_query_str.slice(0, index)
        return clients_query_str
        // return clients_ids
    }

    function gather_dates () {
       let default_value = default_date_value()
       let to = date_to.value
       let from = date_from.value
       if (to) {
           return from +'/'+ to   
       } 
       return  default_value
    }
 
    function send_http_request(date, data) {
        let get_url = location.href.replace(/client\/.*/, 'client/client/') +'account-statment/' + date +"/"+data
        location.replace(get_url) 
    }

    function send_ajax_post(date, data) {
        let ajax = new XMLHttpRequest()
        let post_url = location.href.replace(/client\/.*/, 'client/client/') +'account-statment/'
        post_url+= date
        ajax.open('POST', post_url)
        ajax.setRequestHeader('X-CSRFToken', csrf)
        ajax.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        ajax.onload = function() {
            if (ajax.status == 200) {
                window.Headers['Content-Disposition'] = ajax.getResponseHeader('Content-Disposition') 
                alert('Account statments has succsefully downloaded')
                // return ajax.response 
            }
        }
        ajax.send(JSON.stringify({'clients_ids':data}))
    }
    
  
    function gather_data() {
        let clients_ids = gather_client_ids()
        let full_date =  gather_dates()
        if (clients_ids) {
            // send_ajax_post(full_date, clients_ids)
            send_http_request(full_date, clients_ids)
        }
            
    }
    set_default_date()
    btn.addEventListener('click', gather_data)
}



window.addEventListener('load', start_js) 
