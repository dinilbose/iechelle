import sys
from bokeh.layouts import row, column
# from bokeh.layouts import grid
from bokeh.plotting import curdoc, figure, show
# from bokeh.models import Panel
import pandas
# from bokeh.models import Button  # for saving data
# from bokeh.models.widgets import Tabs
# from bokeh.layouts import layout, Spacer

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
    column(env.stretch_sliderint,
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
    row(env.check_make_grid,
        env.check_show_modes_grid,
        env.check_show_echelle,
        env.grid_circle_size,
        env.check_show_horizontal_lines,
        )
)


tab_interactive_layout = column(row(tab_int_1))


# flag_lay1 = column(env.text_flag_duplicate,
#                    env.text_flag_source,
#                    env.text_flag_check,
#                    env.save_userinput_button)

next_lay1 = row(env.previous_button,
                env.next_button)

next_dflt_lay = column(next_lay1)

# query_lay1 = column(
#                 row(env.text_cluster_query),
#                     env.update_cluster_button,
#                 row(env.text_catalog_query),
#                     env.update_catalog_button,
#                 row(env.int_select_sector),
#                 row(env.text_id_mycatalog_query),
#                     env.update_id_mycatalog_button,
#                 row(env.text_id_query),
#                     env.update_id_button
#                 )

# layer_1 = column(query_lay1,next_dflt_lay)
layer_1 = column(next_dflt_lay)

# notes_lay1 = column(env.text_Notes_w)
layout_catalog = column(
    row(
        env.open_file_button,
        env.selected_filename_text,
    ),
    env.message_banner,
    row(
        tab_interactive_layout,
        column(
            env.fig_other_periodogram,
            row(
                env.inverted_slider,
                env.inverted_line_initial_y_text,
                env.inverted_line_length_text,
                env.inverted_line_scale_text,
                env.inverted_line_xvalue_text,
                env.check_show_inverted_lines,
                env.inverted_line_update_button,
            ),
            row(
                env.table_se_first,
                column(
                    env.test_button,
                    env.find_peaks_button,
                    env.clear_se_table1_button,
                    env.clear_se_grid_prd_button,
                    env.select_mode_menu,
                    env.mode_apply_button,
                    env.move_se_1_2_button,
                    env.move_se_2_1_button,
                ),
                env.table_se_second,
                column(
                    env.load_table_2_button,
                    env.save_table_2_button,
                    env.load_from_specific_file_table_2_button,
                    env.save_as_table_2_button,
                    env.clear_se_table2_button,
                ),
            ),
        )
    ),
sizing_mode="stretch_both",  # Optional: Adjust sizing mode
css_classes=["centered-column"],  
)

# layout_catalog = env.stretch_sliderint
tab_c = TabPanel(child=layout_catalog, title='Mode Selection')
tabs = Tabs(tabs=[tab_c])
curdoc().add_root(tabs)
