
function start_js_transactions() {
    let from    = document.getElementById('transactions_from')
    let to      = document.getElementById('transactions_to')
    let today   = new Date();
    let current_valid_month = get_valid_full_date(today) 
    if (! from) {
        return  
    }

    from.setAttribute('value', current_valid_month)
    to.addEventListener('change', function() {
        let from_value = from.value
        let to_value = to.value
        if (! from_value) {
            from_value  = date
        }
        document.cookie = 'to_value=' + to.value+';'
        document.cookie = 'from_value=' + from_value+';'
        
        location.reload()
    })

    function get_current_moth(today, current_year) {
        let month = today.getMonth()+1
        if  (month < 10) {
            return '0'+ month
        }
    }

    function get_valid_full_date(today) {
        month = get_current_moth(today)
        return today.getFullYear()+'-' +month+ '-01'   
    }

}



window.addEventListener('load', start_js_transactions)  