// $("#modal1").on('hidden.bs.modal', function (e) {
//   // do something...
//   $('#modal1 iframe').attr("src", $("#modal1 iframe").attr("src"));
// });
//
// $('#modal6').on('hidden.bs.modal', function (e) {
//   // do something...
//   $('#modal6 iframe').attr("src", $("#modal6 iframe").attr("src"));
// });
//
// $('#modal4').on('hidden.bs.modal', function (e) {
//   // do something...
//   $('#modal4 iframe').attr("src", $("#modal4 iframe").attr("src"));
// });
$.ajax({
        url: 'http://localhost:8000/list_videos',
        success: function (data) {
            let video_names = data['videos'];
            let str = '';
            elements = document.getElementById('elements');
            console.log(video_names);
            let i = 1;
            video_names.forEach(function (video_name) {
                var para = document.createElement("div");
                para.className = "col-lg-4 col-md-6 mb-4";
                para.innerHTML = `
                    <!-- Grid column -->
<!--                    <div class="col-lg-4 col-md-12 mb-4">-->
                    
                    <!--Modal: Name-->
                    <div class="modal fade" id="modal${i}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
                      <div class="modal-dialog modal-lg" role="document">
                    
                        <!--Content-->
                        <div class="modal-content">
                    
                          <!--Body-->
                          <div class="modal-body mb-0 p-0">
                    
                            <div class="embed-responsive embed-responsive-16by9 z-depth-1-half">
                              <iframe class="embed-responsive-item" src="static/raw/${video_name}"
                                allowfullscreen></iframe>
                            </div>
                    
                          </div>
                    
                          <!--Footer-->
                          <div class="modal-footer justify-content-center">
                            <span class="mr-4">Spread the word!</span>
                            <a type="button" class="btn-floating btn-sm btn-fb"><i class="fab fa-facebook-f"></i></a>
                            <!--Twitter-->
                            <a type="button" class="btn-floating btn-sm btn-tw"><i class="fab fa-twitter"></i></a>
                            <!--Google +-->
                            <a type="button" class="btn-floating btn-sm btn-gplus"><i class="fab fa-google-plus-g"></i></a>
                            <!--Linkedin-->
                            <a type="button" class="btn-floating btn-sm btn-ins"><i class="fab fa-linkedin-in"></i></a>
                    
                            <button type="button" class="btn btn-outline-primary btn-rounded btn-md ml-4" data-dismiss="modal">Close</button>
                    
                          </div>
                    
                        </div>
                        <!--/.Content-->
                    
                      </div>
                    </div>
                    <!--Modal: Name-->
                    
                    <a><img class="img-fluid z-depth-1" src="static/raw/frames/${video_name.slice(0,-4)}.png" alt="video"
                        data-toggle="modal" data-target="#modal${i}"></a>
                    
<!--                    </div>-->
                    <!-- Grid column -->
                                  
                `;
                elements.appendChild(para);
                i+=1;
            });
        },
        error: function (error) {
        }
})
//https://mdbootstrap.com/snippets/jquery/temp/3033883?action=prism_export
