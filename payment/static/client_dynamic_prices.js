'use strict'

function make_prices_dynamic() {
    let field_quantity = 'field-quantity',
    field_cost_per_item  = 'field-cost_per_item_client',
    field_price = 'field-client_price',
    field_cost = 'field-cost',   
    field_item = 'field-item',
    add_now = 'add-row',
    field_discount = 'field-discount',
    items = document.getElementsByClassName(field_item),
    add_new = document.getElementsByClassName(add_now).item(0).lastElementChild.lastElementChild,
    quantity_elements = document.getElementsByClassName(field_quantity),
    cost_elements = document.getElementsByClassName(field_cost_per_item),
    discount_elements = document.getElementsByClassName(field_discount),
    total_cost_element = document.getElementsByClassName(field_cost).item(0).lastElementChild.lastElementChild,
    price_elements = document.getElementsByClassName(field_price);
    

    function calculate_total_cost() {
        let values = []
        for (let cost_of_item of cost_elements) {
            let cost_of_item_value = cost_of_item.innerText
            if (isNaN(cost_of_item_value)){
                continue
            }
            values.push(parseFloat(cost_of_item_value))
        }
        let sum  = Number(values.reduce((a, b) => a + b, 0)).toFixed(2)         
        total_cost_element.innerText = sum
    }

    function link_elments_listeners(elements, elements_to_be_linked_with, to_put_value_in) {
        for (let index in elements) {
            let  element  =  elements.item(index)
            elements.item(index).addEventListener('change', function () {
                let main_value = parseFloat(elements.item(index).lastElementChild.value)
                let secdon_value = parseFloat(elements_to_be_linked_with.item(index).lastElementChild.value)
                
                to_put_value_in.item(index).innerText = Number(main_value * secdon_value).toFixed(2)   
            })
        }

    }

    function attach_listeners () {
        link_elments_listeners(price_elements, quantity_elements, cost_elements)
        link_elments_listeners(quantity_elements, price_elements, cost_elements)
        calculate_total_cost()
    }   

    attach_listeners()
    add_new.addEventListener('click', attach_listeners)
}

window.addEventListener('load', make_prices_dynamic)