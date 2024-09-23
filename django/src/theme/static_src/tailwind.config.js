/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        '../../templates/allauth/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',
        '../../**/templates/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            backgroundImage:
            {
                "synthwave":"url(/static/vecteezy_80s.gif)",
                "najman":"url(/static/najman.webp)",
                "milos":"url(/static/milos2.gif)",
                "trippy":"url(/static/tripy1.gif)",
                "trippy1":"url(/static/tripy2.gif)",
                "dhl":"url(/static/bus.gif)"
            },
            animation:
            {
                "first_stage":"first_place 3s linear infinite",
                "second_stage":"second_place 3s linear infinite",
                "third_stage":"third_place 3s linear infinite",
                "ranking_title":"title 4s linear infinite",
                "size_out_ranking":"size_out_anim 5s ease-in 1",
                "move_cow":"move_across_x_axis 2s linear infinite",
                "move_cow_down":"move_across_y_axis 2s linear infinite",
                "move_cow_both":"move_across_axis 2s linear infinite",
                "mir_move_cow":"mir_move_across_x_axis 2s linear infinite",
                "mir_move_cow_down":"mir_move_across_y_axis 2s linear infinite",
                "mir_move_cow_both":"mir_move_across_axis 2s linear infinite"
            },
            keyframes:
            {
                mir_move_across_axis:{
                    "0%":{
                        right:"0",
                        bottom:"0"
                    },
                    "50%":{
                        right:"100%",
                        bottom:"100%"
                    },
                    "100%":
                    {
                        right:"0",
                        bottom:"0"
                    }
                },
                mir_move_across_x_axis:{
                    "0%":{
                        right:"0"
                    },
                    "50%":{
                        right:"100%"
                    },
                    "100%":
                    {
                        right:"0"
                    }
                },
                mir_move_across_y_axis:{
                    "0%":{
                        bottom:"0"
                    },
                    "50%":{
                        bottom:"100%"
                    },
                    "100%":
                    {
                        bottom:"0"
                    }
                },
                move_across_axis:{
                    "0%":{
                        left:"0",
                        top:"0"
                    },
                    "50%":{
                        left:"100%",
                        top:"100%"
                    },
                    "100%":
                    {
                        left:"0",
                        top:"0"
                    }
                },
                move_across_x_axis:{
                    "0%":{
                        left:"0"
                    },
                    "50%":{
                        left:"100%"
                    },
                    "100%":
                    {
                        left:"0"
                    }
                },
                move_across_y_axis:{
                    "0%":{
                        top:"0"
                    },
                    "50%":{
                        top:"100%"
                    },
                    "100%":
                    {
                        top:"0"
                    }
                },
                size_out_anim:{
                    "0%":{
                        transform:"scale(0.0)"
                    },
                    "100%":{
                        transform:"scale(1.0)"
                    }
                },
                title:{
                    "0%,50%":{
                        color:"#ff78f8"
                    },
                    "20%,80%":
                    {
                        color:"#78d9ff"
                    },
                    "10%,60%":
                    {
                        color:"#ff78bc"
                    },
                    "5%,30%":
                    {
                        color:"#ff7878"
                    },
                    "45%,85%":
                    {
                        color:"#fffd78d3"
                    },
                    "75%,100%":
                    {
                        color:"#78ff83"
                    }
                },
                first_place:{
                    "0%":{
                        color:"#e478ff"
                    },
                    "50%":
                    {
                        color:"#ff78f8"
                    },
                    "100%":
                    {
                        color:"#ff78b7"
                    }
                },
                second_place:{
                    "0%":{
                        color:"#d0ff78"
                    },
                    "50%":
                    {
                        color:"#8fff78"
                    },
                    "100%":
                    {
                        color:"#78ffac"
                    }
                },
                third_place:{
                    "0%":{
                        color:"#78aeff"
                    },
                    "50%":
                    {
                        color:"#7898ff"
                    },
                    "100%":
                    {
                        color:"#ac78ff"
                    }
                }
            }
        },
        colors: {
            // Configure your color palette here
            primary:'#A66E62',
            secondary:'white',
            teritary:'#F4907B',
            quaternary:'#82574D',
            black:"#000000",
            red:"#FF0000"
          }
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
