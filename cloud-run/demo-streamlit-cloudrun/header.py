import streamlit as st
import pathlib
import shutil
from bs4 import BeautifulSoup   

def header(title, sub_title= None):
    inject_ga()

    
    st.set_page_config(
        page_title=title,
        page_icon="vertex-ai.png",
        layout="wide",
    )

    # col1, col2 = st.columns([8, 1])
    # with col1:
    #     st.title(title)

    # with col2:
    #     st.image("vertex-ai.png")
    # st.header("", divider="rainbow")

    st.header(title, divider="rainbow")

    if sub_title is not None:
        st.subheader(sub_title)


    
def inject_ga():
    """Add this in your streamlit app.py
    see https://github.com/streamlit/streamlit/issues/969
    """
    # new tag method
    GA_ID = "google_analytics"
    # NOTE: you should add id="google_analytics" value in the GA script
    # https://developers.google.com/analytics/devguides/collection/analyticsjs
    GA_JS = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-7KGHD03GV1');
</script>


"""
    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    # logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="lxml")

    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)





# bootstrap 4 collapse example
# st.components.v1.html("""
# <!-- Google tag (gtag.js) -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());

#   gtag('config', 'G-7KGHD03GV1');
                      
# </script>
                      
# """)
# script = """ 
# <script type="module">
#   // Import the functions you need from the SDKs you need
  
#   import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-app.js";
#   import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-analytics.js";
#   // TODO: Add SDKs for Firebase products that you want to use
#   // https://firebase.google.com/docs/web/setup#available-libraries

#   // Your web app's Firebase configuration
#   // For Firebase JS SDK v7.20.0 and later, measurementId is optional
#   const firebaseConfig = {
#     apiKey: "AIzaSyBlicYGLYyFhhNLd35wE2JrDVUM4va3thw",
#     authDomain: "ml-demo-384110.firebaseapp.com",
#     databaseURL: "https://ml-demo-384110-default-rtdb.europe-west1.firebasedatabase.app",
#     projectId: "ml-demo-384110",
#     storageBucket: "ml-demo-384110.appspot.com",
#     messagingSenderId: "1008225662928",
#     appId: "1:1008225662928:web:25b205cbca00004af96bd5",
#     measurementId: "G-DSQBJJBYB2"
#   };

#   // Initialize Firebase
#   const app = initializeApp(firebaseConfig);
#   const analytics = getAnalytics(app);

#   </script>
# """ 

# script2 = """
# </script>        
#         <script async src="https://www.googletagmanager.com/gtag/js?id=G-7KGHD03GV1"></script>
#         <script>
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-7KGHD03GV1');
#         </script>
#         """

# st.markdown(script2, unsafe_allow_html=True, allow_javascript=True, allow_html=True)