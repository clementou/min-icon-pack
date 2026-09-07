package io.github.clementou.miniconpack;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends Activity {
    private final ArrayList<String[]> all = new ArrayList<>();
    private final ArrayList<String[]> visible = new ArrayList<>();
    private boolean picking;
    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        picking = "com.novalauncher.THEME".equals(getIntent().getAction())
            || "org.adw.launcher.icons.ACTION_PICK_ICON".equals(getIntent().getAction());
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(getAssets().open("catalog.tsv"), "UTF-8"))) {
            String line;
            while ((line = reader.readLine()) != null) all.add(line.split("\t", 2));
        } catch (Exception e) {
            throw new IllegalStateException("Cannot load bundled icon catalog", e);
        }
        visible.addAll(all);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(32, 35, 40));
        root.setPadding(dp(16), 0, dp(16), 0);
        root.setOnApplyWindowInsetsListener((v, insets) -> {
            v.setPadding(dp(16), insets.getSystemWindowInsetTop(), dp(16), insets.getSystemWindowInsetBottom());
            return insets;
        });
        TextView title = new TextView(this);
        title.setText(picking ? "Choose a Min icon" : "Min Extended");
        title.setTextSize(28); title.setTextColor(Color.WHITE);
        title.setPadding(0, dp(16), 0, dp(8)); root.addView(title);
        TextView subtitle = new TextView(this);
        subtitle.setText(all.size() + " icons · original Min style, continued");
        subtitle.setTextColor(0xffbfc6d0); subtitle.setPadding(0, 0, 0, dp(12)); root.addView(subtitle);
        if (!picking) {
            Button apply = new Button(this); apply.setText("Apply in Nova");
            apply.setOnClickListener(v -> {
                Intent intent = new Intent("com.teslacoilsw.launcher.APPLY_ICON_THEME");
                intent.setPackage("com.teslacoilsw.launcher");
                intent.putExtra("com.teslacoilsw.launcher.extra.ICON_THEME_PACKAGE", getPackageName());
                try { startActivity(intent); }
                catch (ActivityNotFoundException e) {
                    new AlertDialog.Builder(this).setMessage("In Nova Settings, open Look & feel → Icon style → Icon theme, then choose Min Extended.")
                        .setPositiveButton("OK", null).show();
                }
            }); root.addView(apply);
        }
        EditText search = new EditText(this); search.setSingleLine(true);
        search.setHint("Search icons"); search.setTextColor(Color.WHITE); search.setHintTextColor(0xffbfc6d0);
        root.addView(search);
        GridView grid = new GridView(this); grid.setNumColumns(GridView.AUTO_FIT);
        grid.setColumnWidth(dp(100)); grid.setStretchMode(GridView.STRETCH_COLUMN_WIDTH);
        IconAdapter adapter = new IconAdapter(); grid.setAdapter(adapter);
        root.addView(grid, new LinearLayout.LayoutParams(-1, 0, 1));
        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                String query = s.toString().toLowerCase(Locale.ROOT); visible.clear();
                for (String[] entry : all) if ((entry[0]+" "+entry[1]).toLowerCase(Locale.ROOT).contains(query)) visible.add(entry);
                adapter.notifyDataSetChanged();
            }
            public void afterTextChanged(Editable e) {}
        });
        grid.setOnItemClickListener((parent, view, position, id) -> {
            String[] entry = visible.get(position);
            int resource = getResources().getIdentifier(entry[0], "drawable", getPackageName());
            if (picking) {
                Intent result = new Intent();
                result.putExtra(Intent.EXTRA_SHORTCUT_ICON_RESOURCE, Intent.ShortcutIconResource.fromContext(this, resource));
                result.putExtra(Intent.EXTRA_SHORTCUT_ICON, BitmapFactory.decodeResource(getResources(), resource));
                result.setData(Uri.parse("android.resource://" + getPackageName() + "/drawable/" + entry[0]));
                setResult(RESULT_OK, result); finish();
            } else {
                ImageView preview = new ImageView(this); preview.setImageResource(resource);
                preview.setAdjustViewBounds(true); preview.setMaxHeight(dp(192));
                new AlertDialog.Builder(this).setTitle(entry[1]).setView(preview).setPositiveButton("Close",null).show();
            }
        });
        setContentView(root);
        root.requestApplyInsets();
    }

    private class IconAdapter extends BaseAdapter {
        public int getCount() { return visible.size(); }
        public Object getItem(int position) { return visible.get(position); }
        public long getItemId(int position) { return position; }
        public View getView(int position, View recycled, ViewGroup parent) {
            LinearLayout cell;
            if (recycled instanceof LinearLayout) cell = (LinearLayout) recycled;
            else {
                cell = new LinearLayout(MainActivity.this); cell.setOrientation(LinearLayout.VERTICAL);
                cell.setGravity(Gravity.CENTER); cell.setPadding(0,dp(4),0,dp(10));
                ImageView image = new ImageView(MainActivity.this); image.setScaleType(ImageView.ScaleType.FIT_CENTER);
                cell.addView(image, new LinearLayout.LayoutParams(dp(96),dp(96)));
                TextView label = new TextView(MainActivity.this); label.setTextColor(Color.WHITE);
                label.setGravity(Gravity.CENTER); label.setTextSize(11); label.setMaxLines(2);
                cell.addView(label, new LinearLayout.LayoutParams(-1,dp(32)));
            }
            String[] entry = visible.get(position);
            ((ImageView)cell.getChildAt(0)).setImageResource(getResources().getIdentifier(entry[0],"drawable",getPackageName()));
            ((TextView)cell.getChildAt(1)).setText(entry[1]);
            cell.setContentDescription(entry[1]);
            return cell;
        }
    }
}
