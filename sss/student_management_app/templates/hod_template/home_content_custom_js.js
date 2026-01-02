$(document).ready(function(){
  var donutChartCanvas = $('#pieChart').get(0).getContext('2d');
  var pieData = {
    labels: [
        'Students', 
        'Staffs'
    ],
    datasets: [
      {
        data: [0, 0],
        backgroundColor: ['#f56954', '#00a65a']
      }
    ]
  };

  //-------------
  //- PIE CHART -
  //-------------
  // Get context with jQuery - using jQuery's .get() method.
  var pieChartCanvas = $('#pieChart').get(0).getContext('2d');
  var pieOptions = {
    maintainAspectRatio: false,
    responsive: true
  };
  //Create pie or doughnut chart
  // You can switch between pie and doughnut using the method below.
  var pieChart = new Chart(pieChartCanvas, {
    type: 'pie',
    data: pieData,
    options: pieOptions      
  });


  // Get context with jQuery - using jQuery's .get() method.
  var grade_name_list = [];
  var stream_count_list = [];
  var donutChartCanvas = $('#donutChart').get(0).getContext('2d');
  var donutData = {
    labels: grade_name_list,
    datasets: [
      {
        data: stream_count_list,
        backgroundColor: ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']
      }
    ]
  };
  var donutOptions = {
    maintainAspectRatio: false,
    responsive: true
  };
  //Create pie or doughnut chart
  // You can switch between pie and doughnut using the method below.
  var donutChart = new Chart(donutChartCanvas, {
    type: 'doughnut',
    data: donutData,
    options: donutOptions      
  });


  // Total Students in Each grade
  var student_count_list_in_grade = [];
  var pieData2 = {
    labels: grade_name_list,
    datasets: [
      {
        data: student_count_list_in_grade,
        backgroundColor: ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']
      }
    ]
  };

  //-------------
  //- PIE CHART -
  //-------------
  // Get context with jQuery - using jQuery's .get() method.
  var pieChartCanvas2 = $('#pieChart2').get(0).getContext('2d');
  var pieOptions2 = {
    maintainAspectRatio: false,
    responsive: true
  };

  var pieChart2 = new Chart(pieChartCanvas2, {
    type: 'pie',
    data: pieData2,
    options: pieOptions2      
  });

  // Total Students in Each Subject
  var student_count_list_in_stream = [];
  var stream_list = [];
  var pieData3 = {
    labels: stream_list,
    datasets: [
      {
        data: student_count_list_in_stream,
        backgroundColor: ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']
      }
    ]
  };

  //-------------
  //- PIE CHART -
  //-------------
  // Get context with jQuery - using jQuery's .get() method.
  var pieChartCanvas3 = $('#pieChart3').get(0).getContext('2d');
  var pieOptions3 = {
    maintainAspectRatio: false,
    responsive: true
  };

  var pieChart3 = new Chart(pieChartCanvas3, {
    type: 'pie',
    data: pieData3,
    options: pieOptions3      
  });

  //-------------
  //- BAR CHART - Staff Attendance vs Leave
  //-------------

  var staff_attendance_present_list = [];
  var staff_attendance_leave_list = [];
  var staff_name_list = [];

  var areaChartData = {
    labels: staff_name_list,
    datasets: [
      {
        label: 'Leave',
        backgroundColor: 'rgba(60,141,188,0.9)',
        borderColor: 'rgba(60,141,188,0.8)',
        pointRadius: false,
        pointColor: '#3b8bba',
        pointStrokeColor: 'rgba(60,141,188,1)',
        pointHighlightFill: '#fff',
        pointHighlightStroke: 'rgba(60,141,188,1)',
        data: staff_attendance_leave_list
      },
      {
        label: 'Attendance',
        backgroundColor: 'rgba(210, 214, 222, 1)',
        borderColor: 'rgba(210, 214, 222, 1)',
        pointRadius: false,
        pointColor: 'rgba(210, 214, 222, 1)',
        pointStrokeColor: '#c1c7d1',
        pointHighlightFill: '#fff',
        pointHighlightStroke: 'rgba(220,220,220,1)',
        data: staff_attendance_present_list
      }
    ]
  };

  var barChartCanvas = $('#barChart').get(0).getContext('2d');
  var barChartData = jQuery.extend(true, {}, areaChartData);
  var temp0 = areaChartData.datasets[0];
  var temp1 = areaChartData.datasets[1];
  barChartData.datasets[0] = temp1;
  barChartData.datasets[1] = temp0;

  var barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    datasetFill: false
  };

  var barChart = new Chart(barChartCanvas, {
    type: 'bar',
    data: barChartData,
    options: barChartOptions
  });

  //- BAR CHART - Student Attendance vs Leave
  //-------------

  var student_attendance_present_list = [];
  var student_attendance_leave_list = [];
  var student_name_list = [];

  var areaChartData2 = {
    labels: student_name_list,
    datasets: [
      {
        label: 'Leave',
        backgroundColor: 'rgba(60,141,188,0.9)',
        borderColor: 'rgba(60,141,188,0.8)',
        pointRadius: false,
        pointColor: '#3b8bba',
        pointStrokeColor: 'rgba(60,141,188,1)',
        pointHighlightFill: '#fff',
        pointHighlightStroke: 'rgba(60,141,188,1)',
        data: student_attendance_leave_list
      },
      {
        label: 'Attendance',
        backgroundColor: 'rgba(210, 214, 222, 1)',
        borderColor: 'rgba(210, 214, 222, 1)',
        pointRadius: false,
        pointColor: 'rgba(210, 214, 222, 1)',
        pointStrokeColor: '#c1c7d1',
        pointHighlightFill: '#fff',
        pointHighlightStroke: 'rgba(220,220,220,1)',
        data: student_attendance_present_list
      }
    ]
  };

  var barChartCanvas2 = $('#barChart2').get(0).getContext('2d');
  var barChartData2 = jQuery.extend(true, {}, areaChartData2);
  var temp02 = areaChartData2.datasets[0];
  var temp12 = areaChartData2.datasets[1];
  barChartData2.datasets[0] = temp12;
  barChartData2.datasets[1] = temp02;

  var barChartOptions2 = {
    responsive: true,
    maintainAspectRatio: false,
    datasetFill: false
  };

  var barChart2 = new Chart(barChartCanvas2, {
    type: 'bar',
    data: barChartData2,
    options: barChartOptions2
  });

});
