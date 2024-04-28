    let menuHidden=false; 

    window.addEventListener("resize", (event) => {

        const navbar=document.getElementById("navbar");

        if(navbar === null)
        {
            return;
        }

        if(window.innerWidth>786)
        {
            navbar.style.display="flex";
            menuHidden=false;
        }
        else if(!menuHidden)
        {  
            navbar.style.display="none";
            menuHidden=true;
        }
    });

    function toggle()
    {
        const navbar=document.getElementById("navbar");

        if(navbar.style.display == "flex")
        {
            navbar.style.display="none";
        }
        else
        {
            navbar.style.display="flex";
        }
    
    }
