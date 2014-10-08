jQuery(window).load(function() {

  $('input:radio[name="education"]').change(
    function(){
      if ($(this).is(':checked') && (parseInt($(this).val()) > 1)) {
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

});