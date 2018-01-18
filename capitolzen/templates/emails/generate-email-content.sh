#!/bin/bash
rm content/*.html
mjml mjml/simple_action.mjml -o content/simple_action.html
mjml mjml/time_action.mjml -o content/time_action.html
mjml mjml/welcome.mjml -o content/welcome.html
mjml mjml/bill_list.mjml -o content/bill_list.html
