'use strict'

function make_prices_dynamic() {
    let field_quantity = 'field-quantity',
    field_cost_per_item  = 'field-cost_per_item',
    field_price = 'field-price',
    field_cost = 'form-row field-total_cost',
    all_quantities_fields = document.getElementsByClassName(field_quantity),
    all_price_fields = document.getElementsByClassName(field_price),
    all_cost_per_item_fields = document.getElementsByClassName(field_cost_per_item),
    add_new_item = document.getElementsByClassName('add-row').item(0).lastElementChild.lastElementChild,
    total_cost = document.getElementsByClassName(field_cost).item(0).lastElementChild.lastElementChild;

    function get_quantity(index) {
        return all_quantities_fields.item(index).lastElementChild.value
    }

    function multiplay_price_quantity(price, quantity) {
        return Number(parseFloat(price) * parseFloat(quantity)).toFixed(2)
    }
    
    function reflect_cost_per_item(index, new_cost) {
        all_cost_per_item_fields.item(index).lastElementChild.innerText = new_cost
    }

    function get_price(index) {
        return all_price_fields.item(index).lastElementChild.value
    }
    
    function update_cost_item(index, price, quantity) {
       let new_cost = multiplay_price_quantity(price, quantity)
        reflect_cost_per_item(index, new_cost)
    }        
    
    function parse_total_cost(){
        return parseFloat(total_cost.innerText) 
    }

    function add_listeners_to_prices() {
        let index = 0
        let length =  all_price_fields.length
        while (index < length -1) {
            let element = all_price_fields.item(index).lastElementChild
            let element_index = {'index':index, 'element':element}
            element.addEventListener('change', function (){ 
                let quantity    = get_quantity(element_index['index'])
                let price       = element.value
                update_cost_item(element_index['index'], price, quantity)
                assemble_costs()
            })
            index++
        }          
    }

    function assemble_costs() {
        let index = 0
        let cost = 0
        let length =  all_cost_per_item_fields.length
        while (index < length -1) {
            let element = all_cost_per_item_fields.item(index).lastElementChild
            cost += parseFloat(element.innerText)
            index++
        }          
        total_cost.innerText = cost
    }

    function add_listeners_quantities() {
        let index = 0
        let length =  all_quantities_fields.length
        while (index < length -1) {
            let element = all_quantities_fields.item(index).lastElementChild
            let element_index = {'index':index, 'element':element}
            element.addEventListener('change', function (){ 
                let price    = get_price(element_index['index'])
                let quantity       = element.value
                update_cost_item(element_index['index'], price, quantity)
                assemble_costs()
            })
            index++
        }          
    }
    
    add_listeners_to_prices()
    add_listeners_quantities()

    add_new_item.addEventListener('click', function() {
        add_listeners_to_prices()
        add_listeners_quantities()
    })

}

window.addEventListener('load', make_prices_dynamic)