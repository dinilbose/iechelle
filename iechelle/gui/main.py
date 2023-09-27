import sys
from bokeh.layouts import row, column
# from bokeh.layouts import grid
from bokeh.plotting import curdoc, figure, show
# from bokeh.models import Panel
import pandas
# from bokeh.models import Button  # for saving data
# from bokeh.models.widgets import Tabs
# from bokeh.layouts import layout, Spacer
from bokeh.models import Div

from bokeh.models.layouts import TabPanel, Tabs


from catalog import Catalog
from env import Environment
from mode_selection import Interactive

env = Environment


Environment()
Catalog()
Interactive()


nxt_prv_button = row(env.next_button, env.previous_button, sizing_mode='fixed')

tab_int_1 = column(
    # nxt_prv_button,
    column(row(env.stretch_sliderint, env.check_color_map_lock),
           env.fig_tpfint,
           ),
    row(env.ll_button,
        env.l_button,
        env.dnu_slider,
        env.r_button,
        env.rr_button),
    row(env.frequency_minimum_text,
        env.frequency_maximum_text,
        env.frequency_maxdnu_text,
        env.dnu_text,
        env.echelle_noise_cuttoff_text),
    row(env.update_int_button,
        nxt_prv_button,
        env.select_color_palette,
        env.check_reverse_color_palette),
    row(env.select_grid_menu,
        env.check_make_grid,
        env.check_show_modes_grid,
        env.check_show_echelle,
        env.grid_circle_size,
        env.check_show_horizontal_lines,
        )
)


tab_interactive_layout = column(row(tab_int_1))
next_lay1 = row(env.previous_button,
                env.next_button)
next_dflt_lay = column(next_lay1)
layer_1 = column(next_dflt_lay)
extra_plot_lay = row( 
env.open_extra_fits_button,
env.text_extra_plot_name,
env.text_extra_plot_x_init,
env.text_extra_plot_x_scale,
env.text_extra_plot_y_init,
env.text_extra_plot_y_scale,
env.select_extra_plot_color,
env.select_extra_plot_style,
env.open_extra_get_info_button,
env.open_extra_plot_button,
)




layout_catalog = column(
    row(
        env.open_file_button,
        env.selected_filename_text,
    ),
    row(
        env.load_bkg_param_from_file_button,
        env.selected_filename_background_text,
    ),
    row(
        env.load_from_specific_file_table_2_button,
        env.selected_filename_pkb_text,
    ),
    env.message_banner,
    row(
        tab_interactive_layout,
        column(
            env.fig_other_periodogram, 
            row(
                #env.check_periodogram_axis_scale,
                env.inverted_slider,
                env.inverted_line_initial_y_text,
                env.inverted_line_length_text,
                env.inverted_line_scale_text,
                env.inverted_line_xvalue_text,
                env.inverted_slider_max_value_text,
                env.check_show_inverted_lines,
                env.inverted_line_update_button,
            ),
        extra_plot_lay,

            row(
                column(
                        Div(text="<h2 style='text-align: center;'> Table 1 / Selection </h2>", width=500),
                        env.table_se_first,
                        ),
                column(
                    Div(text="",width=150,height=100),
                    env.test_button,
                    env.find_peaks_button,
                    env.clear_se_table1_button,
                    env.clear_se_grid_prd_button,
                    env.select_mode_menu,
                    env.mode_apply_button,
                    env.move_se_1_2_button,
                    env.move_se_2_1_button,
                ),
                column(
                        Div(text="<h2 style='text-align: center;'> Table 2 / Saving", width=500),                
                        env.table_se_second,
                        ),
                column(
                    Div(text="",width=150,height=100),
                    env.load_table_2_button,
                    env.save_table_2_button,
                    env.load_from_specific_file_table_2_button,
                    env.save_as_table_2_button,
                    env.clear_se_table2_button,
                    env.calculate_synthetic_psd_button,
                ),
            ),
        ),
                        column(env.table_plot, 
                               env.show_plot,
                               env.calculate_synthetic_psd_button,
                                ),

    ),

    # column(
    #     Div(text="<h2 style='text-align: center;'> FITS:", width=500),env.selected_filename_text,
    #     env.selected_filename_pkb_text,
    #     env.selected_filename_background_text,
    # ),
    sizing_mode="stretch_both",  # Optional: Adjust sizing mode
    css_classes=["centered-column"],  
)

# layout_catalog = env.stretch_sliderint
tab_c = TabPanel(child=layout_catalog, title='Mode Selection')
tabs = Tabs(tabs=[tab_c])
curdoc().add_root(tabs)
