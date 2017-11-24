<%inherit file="splash_base.mako" />

<%block name="additional_css">
  .faq li {
    margin:10px 0;
  }

  .polymathian {
    margin:30px 0;
  }
</%block>

<%block name="header_title">Prioritise Your City Wish List</%block>

<%block name="app_description">
    <p>This app solves the problem of working out which Cities to visit.</p>
    <ul>
        <li>Enter your list of potential cities with ranks for really important things like how good it is to work or holiday there.</li>
        <li>Enter the average daily spend of each city, you can use something like <a href="https://nomadlist.com/" target="_blank">Nomadlist</a> to get amounts.</li>
        <li>Enter your priorities and desired average daily budget and click solve to get a refined list.</li>
    </ul>
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
