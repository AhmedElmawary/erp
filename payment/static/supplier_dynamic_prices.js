'use strict'

function make_prices_dynamic() {
    let field_quantity = 'field-quantity',
    field_cost_per_item  = 'field-cost_per_item_supplier',
    field_price = 'field-supplier_price',
    field_cost = 'field-supplier_cash_after_transaction',   
    field_item = 'field-item',
    add_now = 'add-row',
    field_discount = 'field-discount',
    supplier_cash_str = 'field-supplier_cash_html',
    items = document.getElementsByClassName(field_item),
    amount = document.getElementById('id_amount'),
    supplier_cash = document.getElementsByClassName(supplier_cash_str).item(0).lastElementChild.lastElementChild,
    quantity_elements = document.getElementsByClassName(field_quantity),
    cost_elements = document.getElementsByClassName(field_cost_per_item),
    discount_elements = document.getElementsByClassName(field_discount),
    total_cost_element = document.getElementsByClassName(field_cost).item(0).lastElementChild.lastElementChild,
    price_elements = document.getElementsByClassName(field_price);
    let add_new = document.getElementsByClassName(add_now).item(0)
    if (! add_new) {
        return
    }
    add_new = add_new.lastElementChild.lastElementChild
        
    function calculate_total_cost() {
        let values = []
        for (let cost_of_item of cost_elements) {
            let cost_of_item_value = cost_of_item.innerText
            if (isNaN(cost_of_item_value)){
                continue
            }
            values.push(Number(cost_of_item_value))
        }
        if (!isNaN(values[values.length-1])) {
            let sum  = Number(values.reduce((a, b) => a + b, 0)).toFixed(2) 
            total_cost_element.innerText =  Number(supplier_cash.innerText) + Number(sum) + Number(amount.value)
            
        }
    }

    function link_elments_listeners(elements, elements_to_be_linked_with, to_put_value_in) {
        let value_after_discount = null
        for (let index=0; index< elements.length; index++) {
            let  element  =  elements.item(index);

            elements.item(index).addEventListener('change', function () {
                let main_value = parseFloat(elements.item(index).lastElementChild.value);
                let secdon_value = parseFloat(elements_to_be_linked_with.item(index).lastElementChild.value);
                let cost_per_item_row = Number(main_value * secdon_value).toFixed(2)   
                to_put_value_in.item(index).innerText = cost_per_item_row 
                let discount_name = 'id_orderitem_set-'+index+'-discount';
                let currnet_discount = document.getElementById(discount_name);
                let discount_value = 0;  
                let discount_text = 0;

                currnet_discount.addEventListener('change', function() {
                    let selected_index = this.options.selectedIndex;
                    let selected_option_list = this.options[selected_index].text.split(" ");
                    let item_length = selected_option_list.length;
                    let is_cash =  item_length > 2  && item_length > 0; 
                    if (is_cash) {
                        value_after_discount = cost_per_item_row -  Number(selected_option_list[0]);
                        to_put_value_in.item(index).innerText = value_after_discount
                    }else if (item_length == 1){
                        to_put_value_in.item(index).innerText = cost_per_item_row 
                    }else{
                        to_put_value_in.item(index).innerText = (cost_per_item_row * Number(selected_option_list[0])) / 100
                    }
                });
                
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