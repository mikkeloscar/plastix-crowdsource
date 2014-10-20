jQuery(window).load(function() {

  $('input:radio[name="education"]').change(
    function(){
      if ($(this).is(':checked') && (parseInt($(this).val()) > 2)) {
        $("#educationfield").show();
      } else {
        $("#educationfield").hide();
      }
    }
  );

  $('input:radio[name="programming"]').change(
    function(){
      if ($(this).is(':checked') && $(this).val() == 'yes') {
        $("#programminglevel, #programminglanguages").show();
      } else {
        $("#programminglevel, #programminglanguages").hide();
      }
    }
  );

  var timer;
  var counter = 0;

  $("#timerarea").focus(function(){
    timer = setInterval(function(){
      counter++;
      $("#timer").html(counter);
    }, 1000);
  });

  $("#submit").click(function(){
    clearInterval(timer);
  });

});