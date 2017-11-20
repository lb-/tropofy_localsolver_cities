<%inherit file="splash_base.mako" />

<%block name="additional_css">
    .faq li {
        margin:10px 0;
    }

    .polymathian {
        margin:30px 0;
    }
</%block>

<%block name="header_title">Knapsack Optimiser</%block>

<%block name="app_description">
    <p>This app solves the well known Knapsack problem. It is defined as follows:</p>
    <ul>
        <li>Given a set of items with weights and values.</li>
        <li>And a 'knapsack' that can hold a certain weight.</li>
        <li>Allocate items to the knapsack, such that the value of the items contained within is maximised.</li>
    </ul>
    <p>Need help or wish this app had more features? Contact us at <b>info@tropofy.com</b> to see if we can help.</p>
</%block>

## Body
<div class="row"></div>

<div class="row"></div>

<div class="row">
    <div class="col-xs-12">
        <div class="polymathian text-center">
        This app was created using the <a href="http://www.tropofy.com" target="_blank">Tropofy platform</a> and is powered by <a href="http://www.localsolver.com/" target="_blank">LocalSolver</a>.
        </div>
    </div>
</div>
