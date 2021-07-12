'use strict'

function start_js_export()  {
    let export_daily_report = document.getElementById('export_daily_report')
    let btn_export_reports = document.getElementById('btn-export-reports')
    let today   = new Date();
    
    if (! export_daily_report) {
        return
    }
    

    function get_current_month(today) {
        let month = today.getMonth()+1
        if  (month < 10) {
            return '0'+ month
        }
    }
    
    function get_current_day(date_obj){
        let current_day = date_obj.getDate();
        if (current_day < 10) {
            current_day = '0'+current_day 
        }     
        return current_day
    
    }
    
    function get_valid_full_date(today) {
        let month = get_current_month(today)
        let day = get_current_day(today)
        return today.getFullYear()+'-' +month+'-'+day
    }
    
    
    let current_valid_month = get_valid_full_date(today)
    export_daily_report.value = current_valid_month
    

    export_daily_report.setAttribute('max', current_valid_month)

    btn_export_reports.addEventListener('click', function(event){
        let export_daily_report_value  = export_daily_report.value
        
        if (! export_daily_report_value) {
            export_daily_report_value = current_valid_month
        }
        document.cookie = 'export_reports_for=' + export_daily_report_value+ ";"
        let url  = window.location.href+btn_export_reports.getAttribute('href');

        window.open(url,'print',"toolbar=no,scrollbars=yes,resizable=0,top=100,left=100,width=595,height=842")
        event.preventDefault();
    })
}

window.addEventListener('load', start_js_export)